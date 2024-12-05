# vCenter Manager

A Flask-based web application for managing VMware vCenter infrastructure. This application provides a modern, user-friendly interface for managing virtual machines, monitoring cluster statistics, and performing common VM operations.

## Features

- Dashboard with cluster statistics
- VM Management:
  - View all VMs and their status
  - Power operations (on/off/reset)
  - Configure VM resources (CPU, Memory)
  - Delete VMs
  - Create VMs from templates
- Modern, responsive UI using Tailwind CSS
- Secure credential management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bourman/vcenter-manager.git
cd vcenter-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure vCenter credentials:
```bash
cp .env.template .env
# Edit .env with your vCenter credentials
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Configuration

Edit the `.env` file with your vCenter credentials:
```
VCENTER_HOST=your_vcenter_ip_or_hostname
VCENTER_USER=your_username
VCENTER_PASSWORD=your_password
```

## Requirements

- Python 3.7+
- Flask
- PyVmomi (VMware vSphere API Python Bindings)
- Access to a VMware vCenter server

## License

MIT License
