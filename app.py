from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import atexit
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

def get_vcenter_connection():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE
    
    service_instance = SmartConnect(
        host=os.getenv('VCENTER_HOST'),
        user=os.getenv('VCENTER_USER'),
        pwd=os.getenv('VCENTER_PASSWORD'),
        sslContext=context
    )
    atexit.register(Disconnect, service_instance)
    return service_instance

def get_all_vms(content):
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )
    return container.view

def get_cluster_stats(content):
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.ComputeResource], True
    )
    stats = {
        'total_clusters': 0,
        'total_hosts': 0,
        'total_cpu_cores': 0,
        'total_memory_gb': 0,
        'total_vms': 0
    }
    
    for cluster in container.view:
        stats['total_clusters'] += 1
        stats['total_hosts'] += len(cluster.host)
        for host in cluster.host:
            stats['total_cpu_cores'] += host.hardware.cpuInfo.numCpuCores
            stats['total_memory_gb'] += host.hardware.memorySize / (1024**3)
        stats['total_vms'] += len(cluster.vm)
    
    return stats

@app.route('/')
def index():
    try:
        si = get_vcenter_connection()
        content = si.RetrieveContent()
        
        # Get VMs
        vms = get_all_vms(content)
        vm_list = [{
            'name': vm.name,
            'power_state': vm.runtime.powerState,
            'cpu': vm.config.hardware.numCPU,
            'memory_gb': vm.config.hardware.memoryMB / 1024,
            'guest_os': vm.config.guestFullName
        } for vm in vms]
        
        # Get cluster stats
        cluster_stats = get_cluster_stats(content)
        
        return render_template('index.html', vms=vm_list, stats=cluster_stats)
    except Exception as e:
        flash(f"Error connecting to vCenter: {str(e)}", "error")
        return render_template('index.html', vms=[], stats={})

@app.route('/vm/<vm_name>/power', methods=['POST'])
def power_operation(vm_name):
    action = request.form.get('action')
    try:
        si = get_vcenter_connection()
        content = si.RetrieveContent()
        vms = get_all_vms(content)
        
        target_vm = next((vm for vm in vms if vm.name == vm_name), None)
        if not target_vm:
            return jsonify({'error': 'VM not found'}), 404
            
        if action == 'on' and target_vm.runtime.powerState == 'poweredOff':
            target_vm.PowerOnVM_Task()
        elif action == 'off' and target_vm.runtime.powerState == 'poweredOn':
            target_vm.PowerOffVM_Task()
        elif action == 'reset' and target_vm.runtime.powerState == 'poweredOn':
            target_vm.ResetVM_Task()
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vm/<vm_name>/config', methods=['POST'])
def update_vm_config(vm_name):
    try:
        si = get_vcenter_connection()
        content = si.RetrieveContent()
        vms = get_all_vms(content)
        
        target_vm = next((vm for vm in vms if vm.name == vm_name), None)
        if not target_vm:
            return jsonify({'error': 'VM not found'}), 404
            
        config_spec = vim.vm.ConfigSpec()
        
        # Update CPU if specified
        new_cpu = request.form.get('cpu')
        if new_cpu:
            config_spec.numCPUs = int(new_cpu)
            
        # Update Memory if specified
        new_memory = request.form.get('memory')
        if new_memory:
            config_spec.memoryMB = int(float(new_memory) * 1024)
            
        task = target_vm.ReconfigVM_Task(spec=config_spec)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vm/<vm_name>/delete', methods=['POST'])
def delete_vm(vm_name):
    try:
        si = get_vcenter_connection()
        content = si.RetrieveContent()
        vms = get_all_vms(content)
        
        target_vm = next((vm for vm in vms if vm.name == vm_name), None)
        if not target_vm:
            return jsonify({'error': 'VM not found'}), 404
            
        if target_vm.runtime.powerState == 'poweredOn':
            task = target_vm.PowerOffVM_Task()
            
        task = target_vm.Destroy_Task()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
