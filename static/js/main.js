// Main JavaScript for vCenter Manager

// VM Management Functions
class VMManager {
    static async powerOperation(vmName, action) {
        try {
            const formData = new FormData();
            formData.append('action', action);
            
            const response = await fetch(`/vm/${vmName}/power`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                location.reload();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to perform power operation');
            }
        } catch (error) {
            this.showError('Error performing power operation');
        }
    }

    static async deleteVM(vmName) {
        if (!confirm(`Are you sure you want to delete ${vmName}?`)) {
            return;
        }

        try {
            const response = await fetch(`/vm/${vmName}/delete`, {
                method: 'POST'
            });
            
            if (response.ok) {
                location.reload();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to delete VM');
            }
        } catch (error) {
            this.showError('Error deleting VM');
        }
    }

    static async updateVMConfig(vmName, config) {
        try {
            const formData = new FormData();
            if (config.cpu) formData.append('cpu', config.cpu);
            if (config.memory) formData.append('memory', config.memory);
            
            const response = await fetch(`/vm/${vmName}/config`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                location.reload();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to update VM configuration');
            }
        } catch (error) {
            this.showError('Error updating VM configuration');
        }
    }

    static showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-4 right-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }
}

// Initialize tooltips and other UI elements
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for modals
    const modals = document.querySelectorAll('[data-modal-toggle]');
    modals.forEach(trigger => {
        const modalId = trigger.dataset.modalToggle;
        const modal = document.getElementById(modalId);
        
        trigger.addEventListener('click', () => {
            modal.classList.toggle('hidden');
        });
    });

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-backdrop')) {
            e.target.classList.add('hidden');
        }
    });
});
