#!/usr/bin/env python3

import asyncio
import json
import logging
import os
import threading
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP
import bbot
from bbot import Scanner, Preset

# Set environment variables to prevent any interactive prompts
os.environ['SUDO_ASKPASS'] = '/bin/false'      # Make sudo fail non-interactively
os.environ['BBOT_SUDO_PASS'] = 'skip'          # Skip sudo prompts in bbot
os.environ['DEBIAN_FRONTEND'] = 'noninteractive'  # Prevent dpkg/apt prompts
os.environ['NEEDRESTART_MODE'] = 'a'           # Auto-restart services (Ubuntu)
os.environ['PYTHONUNBUFFERED'] = '1'           # Unbuffered output
os.environ['CI'] = 'true'                      # Signal this is CI/automated environment

# Additional aggressive dependency prevention
os.environ['BBOT_DEPS_BEHAVIOR'] = 'ignore'    # Force bbot to ignore dependencies
os.environ['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'  # Disable pip version checks
os.environ['PIP_NO_DEPS'] = '1'                # Prevent pip from installing dependencies


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BbotScanManager:
    """Manages bbot scans with async support"""
    
    def __init__(self):
        self.active_scans: Dict[str, Dict] = {}
        self.scan_results: Dict[str, List] = {}
        
    def start_scan(self, scan_id: str, targets: List[str], modules: List[str] = None, 
                   presets: List[str] = None, flags: List[str] = None, no_deps: bool = True) -> Dict:
        """Start a bbot scan in a separate thread"""
        try:
            scan_config = {
                'id': scan_id,
                'targets': targets,
                'modules': modules or [],
                'presets': presets or [],
                'flags': flags or [],
                'no_deps': no_deps,
                'status': 'starting',
                'start_time': datetime.now().isoformat(),
                'results': []
            }
            
            self.active_scans[scan_id] = scan_config
            self.scan_results[scan_id] = []
            
            # Start scan in separate thread
            thread = threading.Thread(target=self._run_scan, args=(scan_id,))
            thread.daemon = True
            thread.start()
            
            return {'success': True, 'scan_id': scan_id, 'status': 'started'}
            
        except Exception as e:
            logger.error(f"Error starting scan {scan_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_scan(self, scan_id: str):
        """Run bbot scan in thread"""
        try:
            # Redirect stdin to prevent any interactive prompts
            import sys
            original_stdin = sys.stdin
            sys.stdin = open(os.devnull, 'r')
            
            scan_config = self.active_scans[scan_id]
            scan_config['status'] = 'running'
            
            # Create preset
            preset = Preset()
            
            # Add presets if specified
            for preset_name in scan_config.get('presets', []):
                preset.include_preset(preset_name)
            
            # Add modules if specified
            if scan_config.get('modules'):
                for module_name in scan_config['modules']:
                    preset.add_module(module_name)
            
            # Add flags if specified (extend existing flags, don't replace)
            if scan_config.get('flags'):
                existing_flags = set(preset.flags) if preset.flags else set()
                new_flags = set(scan_config['flags'])
                preset.flags = list(existing_flags.union(new_flags))
            
            # Exclude problematic modules that cause dependency issues
	    # problematic_modules = ['trufflehog', 'sslcert']  # Known problematic modules
            problematic_modules = str.split(os.environ.get("BBOT_EXCLUDE_MODULES",""),",")  # Known problematic modules
            if hasattr(preset, 'exclude_modules'):
                existing_exclusions = set(preset.exclude_modules) if preset.exclude_modules else set()
                preset.exclude_modules = list(existing_exclusions.union(set(problematic_modules)))
            else:
                preset.exclude_modules = problematic_modules
            
            # Configure comprehensive dependency prevention to avoid sudo prompts
            deps_config = {}
            if scan_config.get('no_deps', True):
                deps_config = {
                    'deps': {'behavior': 'ignore'},
                    'force_deps': False,
                    'install_deps': False,
                    'auto_install_deps': False,
                    'check_deps': False,
                    'retry_deps': False,
                    'ignore_failed_deps': True,
                    'force': True  # Force modules to run even if dependencies fail
                }
            
            # Create scanner with comprehensive dependency prevention configuration
            scanner = Scanner(*scan_config['targets'], preset=preset, config=deps_config)
            
            # Run scan and collect results
            results = []
            for event in scanner.start():
                # Safely serialize event attributes
                module_name = ''
                try:
                    module_attr = getattr(event, 'module', '')
                    module_name = str(module_attr) if module_attr else ''
                except:
                    module_name = 'unknown'
                
                tags_list = []
                try:
                    tags_attr = getattr(event, 'tags', [])
                    tags_list = list(tags_attr) if tags_attr else []
                except:
                    tags_list = []
                
                result = {
                    'type': event.type,
                    'data': str(event.data),
                    'host': getattr(event, 'host', ''),
                    'timestamp': datetime.now().isoformat(),
                    'module': module_name,
                    'tags': tags_list
                }
                results.append(result)
                self.scan_results[scan_id].append(result)
            
            # Update scan status
            scan_config['status'] = 'completed'
            scan_config['end_time'] = datetime.now().isoformat()
            scan_config['total_results'] = len(results)
            
            logger.info(f"Scan {scan_id} completed with {len(results)} results")
            
        except Exception as e:
            logger.error(f"Error running scan {scan_id}: {str(e)}")
            scan_config['status'] = 'error'
            scan_config['error'] = str(e)
        finally:
            # Restore original stdin
            try:
                sys.stdin.close()
                sys.stdin = original_stdin
            except:
                pass
    
    def get_scan_status(self, scan_id: str) -> Dict:
        """Get status of a scan"""
        if scan_id not in self.active_scans:
            return {'success': False, 'error': 'Scan not found'}
        
        scan_info = self.active_scans[scan_id].copy()
        scan_info['result_count'] = len(self.scan_results.get(scan_id, []))
        return {'success': True, 'scan': scan_info}
    
    def get_scan_results(self, scan_id: str, limit: int = None) -> Dict:
        """Get results from a scan"""
        if scan_id not in self.active_scans:
            return {'success': False, 'error': 'Scan not found'}
        
        results = self.scan_results.get(scan_id, [])
        if limit:
            results = results[:limit]
        
        return {
            'success': True,
            'scan_id': scan_id,
            'results': results,
            'total_count': len(self.scan_results.get(scan_id, []))
        }
    
    def list_active_scans(self) -> Dict:
        """List all active scans"""
        scans = []
        for scan_id, scan_info in self.active_scans.items():
            scan_summary = {
                'id': scan_id,
                'status': scan_info['status'],
                'targets': scan_info['targets'],
                'start_time': scan_info['start_time'],
                'result_count': len(self.scan_results.get(scan_id, []))
            }
            scans.append(scan_summary)
        
        return {'success': True, 'scans': scans}


# Initialize MCP server and scan manager
mcp = FastMCP("BBOT Scanner")
scan_manager = BbotScanManager()


@mcp.tool()
def list_bbot_modules() -> str:
    """List all available bbot modules"""
    try:
        preset = Preset()
        all_modules = list(preset.module_loader.all_module_choices)
        
        # Categorize modules (simplified approach)
        scan_modules = []
        output_modules = []
        internal_modules = []
        
        for module_name in all_modules:
            # Basic categorization - output modules typically have 'output' in name
            if 'output' in module_name.lower():
                output_modules.append({
                    'name': module_name,
                    'description': f'{module_name} module',
                    'type': 'output'
                })
            elif module_name in ['stats', 'csv', 'json', 'txt', 'neo4j', 'webhooks']:
                output_modules.append({
                    'name': module_name,
                    'description': f'{module_name} output module',
                    'type': 'output'
                })
            else:
                scan_modules.append({
                    'name': module_name,
                    'description': f'{module_name} scan module',
                    'type': 'scan'
                })
        
        result = {
            'success': True,
            'modules': {
                'scan_modules': scan_modules,
                'output_modules': output_modules,
                'internal_modules': internal_modules
            },
            'total_count': len(all_modules)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing modules: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


@mcp.tool()
def list_bbot_presets() -> str:
    """List all available bbot presets"""
    try:
        preset = Preset()
        all_presets = preset.all_presets
        
        preset_list = []
        for preset_name, preset_tuple in all_presets.items():
            # preset_tuple is (preset_obj, description, path, yml_path)
            description = preset_tuple[1] if len(preset_tuple) > 1 and preset_tuple[1] else f'{preset_name} preset'
            preset_list.append({
                'name': preset_name,
                'description': description
            })
        
        return json.dumps({
            'success': True,
            'presets': sorted(preset_list, key=lambda x: x['name']),
            'total_count': len(preset_list)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing presets: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


@mcp.tool()
def start_bbot_scan(targets: str, modules: str = "", presets: str = "", flags: str = "", no_deps: bool = True) -> str:
    """
    Start a new bbot scan
    
    Args:
        targets: Comma-separated list of targets (domains, IPs, URLs)
        modules: Comma-separated list of modules to use (optional)
        presets: Comma-separated list of presets to use (optional)
        flags: Comma-separated list of flags to use (optional)
        no_deps: Disable dependency installation to prevent sudo prompts (default: True)
    """
    try:
        # Parse inputs
        target_list = [t.strip() for t in targets.split(',') if t.strip()]
        module_list = [m.strip() for m in modules.split(',') if m.strip()] if modules else []
        preset_list = [p.strip() for p in presets.split(',') if p.strip()] if presets else []
        flag_list = [f.strip() for f in flags.split(',') if f.strip()] if flags else []
        
        if not target_list:
            return json.dumps({'success': False, 'error': 'No targets provided'})
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Start scan
        result = scan_manager.start_scan(
            scan_id=scan_id,
            targets=target_list,
            modules=module_list,
            presets=preset_list,
            flags=flag_list,
            no_deps=no_deps
        )
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


@mcp.tool()
def get_scan_status(scan_id: str) -> str:
    """Get the status of a specific scan"""
    try:
        result = scan_manager.get_scan_status(scan_id)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting scan status: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


@mcp.tool()
def get_scan_results(scan_id: str, limit: int = 100) -> str:
    """
    Get results from a specific scan
    
    Args:
        scan_id: The ID of the scan
        limit: Maximum number of results to return (default: 100)
    """
    try:
        result = scan_manager.get_scan_results(scan_id, limit)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting scan results: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


@mcp.tool()
def list_active_scans() -> str:
    """List all active scans"""
    try:
        result = scan_manager.list_active_scans()
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing active scans: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


@mcp.tool()
def wait_for_scan_completion(scan_id: str, timeout: int = 300, poll_interval: int = 5, include_progress: bool = True) -> str:
    """
    Wait for a scan to complete with timeout and progress reporting
    
    Args:
        scan_id: The ID of the scan to wait for
        timeout: Maximum time to wait in seconds (default: 300 = 5 minutes)
        poll_interval: How often to check scan status in seconds (default: 5)
        include_progress: Whether to include progress updates in the response (default: True)
    """
    try:
        import time
        
        start_time = time.time()
        progress_updates = []
        last_result_count = 0
        
        logger.info(f"Waiting for scan {scan_id} to complete (timeout: {timeout}s, poll: {poll_interval}s)")
        
        while time.time() - start_time < timeout:
            # Get current scan status
            status_result = scan_manager.get_scan_status(scan_id)
            
            if not status_result.get('success'):
                return json.dumps({
                    'success': False, 
                    'error': f"Failed to get scan status: {status_result.get('error')}"
                })
            
            scan_info = status_result.get('scan', {})
            status = scan_info.get('status')
            result_count = scan_info.get('result_count', 0)
            elapsed_time = int(time.time() - start_time)
            
            # Log progress if results changed or every 30 seconds
            if include_progress and (result_count != last_result_count or elapsed_time % 30 == 0):
                progress_update = {
                    'timestamp': datetime.now().isoformat(),
                    'elapsed_seconds': elapsed_time,
                    'status': status,
                    'result_count': result_count,
                    'new_results': result_count - last_result_count
                }
                progress_updates.append(progress_update)
                last_result_count = result_count
                
                logger.info(f"Scan {scan_id} progress: {status}, {result_count} results, {elapsed_time}s elapsed")
            
            # Check if scan is complete
            if status in ['completed', 'error']:
                final_result = {
                    'success': True,
                    'scan_id': scan_id,
                    'final_status': status,
                    'total_results': result_count,
                    'elapsed_seconds': elapsed_time,
                    'completed_naturally': True
                }
                
                if include_progress:
                    final_result['progress_updates'] = progress_updates
                
                if status == 'completed':
                    final_result['message'] = f"Scan completed successfully with {result_count} results in {elapsed_time} seconds"
                else:
                    final_result['message'] = f"Scan failed with error status after {elapsed_time} seconds"
                    final_result['error_details'] = scan_info.get('error', 'Unknown error')
                
                return json.dumps(final_result, indent=2)
            
            # Wait before next check
            time.sleep(poll_interval)
        
        # Timeout reached
        final_status_result = scan_manager.get_scan_status(scan_id)
        final_scan_info = final_status_result.get('scan', {}) if final_status_result.get('success') else {}
        
        timeout_result = {
            'success': False,
            'scan_id': scan_id,
            'error': 'Timeout reached while waiting for scan completion',
            'timeout_seconds': timeout,
            'final_status': final_scan_info.get('status', 'unknown'),
            'final_result_count': final_scan_info.get('result_count', 0),
            'completed_naturally': False
        }
        
        if include_progress:
            timeout_result['progress_updates'] = progress_updates
        
        logger.warning(f"Scan {scan_id} wait timed out after {timeout} seconds")
        return json.dumps(timeout_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error waiting for scan completion: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


@mcp.tool()
def get_dependency_info() -> str:
    """Get information about dependency management in bbot scans"""
    try:
        info = {
            'success': True,
            'dependency_management': {
                'description': 'bbot can automatically install missing dependencies for modules',
                'default_behavior': 'no_deps=True (dependencies disabled by default)',
                'protection_measures': [
                    'deps.behavior=ignore - Skip dependency installation',
                    'force_deps=False - Disable forced dependency installation',
                    'install_deps=False - Disable automatic installation',
                    'check_deps=False - Skip dependency checking',
                    'SUDO_ASKPASS=/bin/false - Make sudo fail non-interactively',
                    'DEBIAN_FRONTEND=noninteractive - Prevent package manager prompts',
                    'stdin redirection to /dev/null - Block all interactive input'
                ],
                'environment_variables': {
                    'SUDO_ASKPASS': os.environ.get('SUDO_ASKPASS', 'not set'),
                    'DEBIAN_FRONTEND': os.environ.get('DEBIAN_FRONTEND', 'not set'), 
                    'CI': os.environ.get('CI', 'not set'),
                    'BBOT_SUDO_PASS': os.environ.get('BBOT_SUDO_PASS', 'not set')
                },
                'sudo_prevention': 'Multiple layers of protection prevent sudo password prompts',
                'recommendation': 'All protection measures are automatically enabled - no action needed'
            }
        }
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting dependency info: {str(e)}")
        return json.dumps({'success': False, 'error': str(e)})


def main():
    """Main entry point for the bbot-mcp-server command."""
    mcp.run()


if __name__ == "__main__":
    main()
