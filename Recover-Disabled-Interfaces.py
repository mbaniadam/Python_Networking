from netmiko import ConnectHandler, ssh_exception
from time import sleep
import subprocess
import getpass
import time
import sys


# function to connect device and get interface status
def get_ports(network_devices):
    """Connection to device to get current port statused"""
    for device in network_devices:
        try:  
            Connect_to_device = ConnectHandler(**device)
            Connect_to_device.enable()
            find_err_ints = Connect_to_device.send_command('Show interface status err-disabled')
            print(find_err_ints)
            for interface in find_err_ints.splitlines():
                if 'psecure-violation' in interface:
                    print ('\n----------- Found disabled interface cause of "p-secure" -----------')
                    _connect_fix_print_psecure_ports(interface, Connect_to_device)
                elif 'bpduguard' in interface:
                    print ('\n\n\n----------- Found disabled interface cause of "bpduguard" -----------')
                    _connect_fix_print_bpduguard_ports(interface, Connect_to_device)
                elif 'loopback' in interface:
                    print ('\n\n\n----------- Found disabled interface cause of "loopback" -----------')
                    _connect_fix_print_loopback_ports(interface, Connect_to_device)
                elif 'dhcp-rate-limit' in interface:
                    print ('\n\n\n----------- Found disabled interface cause of "dhcp-rate-limit" -----------')
                    _connect_fix_print_bpduguard_ports(interface, Connect_to_device)
                          
        except (ssh_exception.AuthenticationException, EOFError):
                print(f'Authentication Error Device: {host} . Authentication Error')
        except ssh_exception.NetmikoTimeoutException:
                print(f'Could not connect to {host} . Reason: Connection Timeout')  

# Function for bpduguard violation
def _connect_fix_print_bpduguard_ports(interface, Connect_to_device):
    try:
            try:
                To_Excecute = Connect_to_device.send_config_set([f'interface {interface.split()[0]}' ,'shut','no shut'])
                _loading()
                print('interface shutdown and no shutdown')
                To_Excecute = Connect_to_device.send_command(f'show interfaces {interface.split()[0]} status')
                if 'err-disabled' in To_Excecute:
                    print('interface still disabled!')
                else:
                    print('\n-------------------------------- interfaces status -------------------------------- ')
                    print(To_Excecute)
                    print("--------------------------------------------------------------------------------------")
            except (ssh_exception.AuthenticationException, EOFError):
                print(f'Authentication Error Device. Authentication Error')
            except ssh_exception.NetmikoTimeoutException:
                print(f'Could not connect. Reason: Connection Timeout')

    except IndexError:
        pass

# Function for p-secure violation
def _connect_fix_print_psecure_ports(interface, Connect_to_device):
    try:
            try:
                Connect_to_device.send_command(f'clear port-security sticky interface {interface.split()[0]}')
                To_Excecute = Connect_to_device.send_config_set([f'interface {interface.split()[0]}' ,'shut','no shut'])
                _loading()
                print('MAC address cleared from interface!')
                print('interface shutdown and no shutdown')
                To_Excecute = Connect_to_device.send_command(f'show interfaces {interface.split()[0]} status')
                if 'err-disabled' in To_Excecute:
                    print('MAC address cleared but interface still in err-disabled status!\nTrying to clear all sticky MAC address ...')
                    Connect_to_device.send_command('clear port-security sticky')
                    Connect_to_device.send_config_set([f'interface {interface.split()[0]}' ,'shut','no shut'])
                    _loading()
                    To_Excecute = Connect_to_device.send_command(f'show interfaces {interface.split()[0]} status')
                    print('All Sticky MAC addresses cleared!')
                    print('\n-------------------------------- interfaces status -------------------------------- ')
                    print(To_Excecute)
                else:
                    print('\n-------------------------------- interfaces status -------------------------------- ')
                    print(To_Excecute)
                    print("--------------------------------------------------------------------------------------")
            except (ssh_exception.AuthenticationException, EOFError):
                print(f'Authentication Error Device. Authentication Error')
            except ssh_exception.NetmikoTimeoutException:
                print(f'Could not connect. Reason: Connection Timeout')

    except IndexError:
        pass

# Function for loopback violation
def _connect_fix_print_loopback_ports(interface, Connect_to_device):
    try:
            try:
                To_Excecute = Connect_to_device.send_config_set([f'interface {interface.split()[0]}' ,'shut','no shut'])
                _loading()
                print('interface shutdown and no shutdown')
                print(To_Excecute)
                if 'err-disabled' in To_Excecute:
                    print('Interface still in Loopback Error!\nThe source interface receives the keepalive packet that it sent out!')
                else:
                    To_Excecute = Connect_to_device.send_command(f'show interfaces {interface.split()[0]} status')
                    print(To_Excecute)
            except ssh_exception.NetmikoTimeoutException:
                print(f'Could not connect. Reason: Connection Timeout')

    except IndexError:
        pass


#Function for loading
def _loading():
    print("Working! ")
    #animation = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
    animation = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]", "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]"]

    for i in range(len(animation)):
        time.sleep(0.3)
        sys.stdout.write("\r" + animation[i % len(animation)])
        sys.stdout.flush()
    print("\n")


print('Please enter Device IP address: ')
host = (str(input()))
print('Please enter your username: ')
get_username = (str(input()))
get_pass = getpass.getpass(prompt='Please enter your password: ', stream=None) 
print('Please Wait...')
network_devices = [{'host':host,'username':'get_username','password':'get_pass','device_type':'cisco_ios'}]

get_ports(network_devices):
print("\n-------------------------- End --------------------------")
