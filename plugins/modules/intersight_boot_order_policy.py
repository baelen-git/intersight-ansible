#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: intersight_boot_order_policy
short_description: Boot Order policy configuration for Cisco Intersight
description:
  - Boot Order policy configuration for Cisco Intersight.
  - Used to configure Boot Order servers and timezone settings on Cisco Intersight managed devices.
  - For more information see L(Cisco Intersight,https://intersight.com/apidocs).
extends_documentation_fragment: intersight
options:
  state:
    description:
      - If C(present), will verify the resource is present and will create if needed.
      - If C(absent), will verify the resource is absent and will delete if needed.
    choices: [present, absent]
    default: present
  organization:
    description:
      - The name of the Organization this resource is assigned to.
      - Profiles and Policies that are created within a Custom Organization are applicable only to devices in the same Organization.
    default: default
  name:
    description:
      - The name assigned to the Boot Order policy.
      - The name must be between 1 and 62 alphanumeric characters, allowing special characters :-_.
    required: true
  tags:
    description:
      - List of tags in Key:<user-defined key> Value:<user-defined value> format.
    type: list
  description:
    description:
      - The user-defined description of the Boot Order policy.
      - Description can contain letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), or an underscore(_).
    aliases: [descr]
  configured_boot_mode:
    description:
      - Sets the BIOS boot mode.
      - UEFI uses the GUID Partition Table (GPT) whereas Legacy mode uses the Master Boot Record (MBR) partitioning scheme.
    choices: [Legacy, Uefi]
    default: Legacy
  uefi_enable_secure_boot:
    description:
      - Secure boot enforces that device boots using only software that is trusted by the Original Equipment Manufacturer (OEM).
      - Option is only used if configured_boot_mode is set to Uefi.
    type: bool
    default: false
  boot_devices:
    description:
      - List of Boot Devices configured on the endpoint.
    type: list
    suboptions:
      enabled:
        description:
          - Specifies if the boot device is enabled or disabled.
        type: bool
        default: true
      device_type:
        description:
          - Device type used with this boot option.
        choices: [local_disk, virtual_media]
        required: true
      device_name:
        description:
          - A name that helps identify a boot device.
          - It can be any string that adheres to the following constraints.
          - It should start and end with an alphanumeric character.
          - It can have underscores and hyphens.
          - It cannot be more than 30 characters.
        required: true
      controller_slot:
        description:
          - The slot id of the controller for the local disk device.
          - Option is used when device_type is local_disk.
        choices: [1-255, M, HBA, SAS, RAID, MRAID, MSTOR-RAID]
      bootloader_name:
        description:
          - Details of the bootloader to be used during boot from local disk.
          - Option is used when device_type is local_disk and configured_boot_mode is Uefi.
      bootloader_description:
        description:
          - Details of the bootloader to be used during boot from local disk.
          - Option is used when device_type is local_disk and configured_boot_mode is Uefi.
      bootloader_path:
        description:
          - Details of the bootloader to be used during boot from local disk.
          - Option is used when device_type is local_disk and configured_boot_mode is Uefi.
      virtual_media_subtype:
        description:
          - The subtype for the selected device type.
          - Option is used when device_type is virtual_media.
        choices: [None, cimc-mapped-dvd, cimc-mapped-hdd, kvm-mapped-dvd, kvm-mapped-hdd, kvm-mapped-fdd]
        default: None
author:
  - Tse Kai "Kevin" Chan (@BrightScale)
version_added: '2.10'
'''

EXAMPLES = r'''
- name: Configure Boot Order Policy
  cisco.intersight.intersight_boot_order_policy:
    api_private_key: "{{ api_private_key }}"
    api_key_id: "{{ api_key_id }}"
    organization: DevNet
    name: COS-Boot
    description: Boot Order policy for COS
    tags:
      - Key: Site
        Value: RCDN
    configured_boot_mode: legacy
    boot_devices:
      - device_type: local_disk
        device_name: Boot-Lun
        controller_slot: MRAID

- name: Delete Boot Order Policy
  cisco.intersight.intersight_boot_policy:
    api_private_key: "{{ api_private_key }}"
    api_key_id: "{{ api_key_id }}"
    organization: DevNet
    name: COS-Boot
    state: absent
'''

RETURN = r'''
api_repsonse:
  description: The API response output returned by the specified resource.
  returned: always
  type: dict
  sample:
    "api_response": {
        "Name": "COS-Boot",
        "ObjectType": "boot.Policy",
        "Tags": [
            {
                "Key": "Site",
                "Value": "RCDN"
            }
        ]
    }
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.intersight.plugins.module_utils.intersight import IntersightModule, intersight_argument_spec, compare_values


def main():
    boot_device = dict(
        enabled=dict(type='bool', default=True),
        device_type=dict(
            type='str',
            choices=[
                'iscsi',
                'local_cdd',
                'local_disk',
                'nvme',
                'pch_storage',
                'pxe',
                'san',
                'sd_card',
                'uefi_shell',
                'usb',
                'virtual_media'
            ],
            required=True,
        ),
        device_name=dict(type='str', required=True),
        # iscsi and pxe options
        network_slot=dict(type='str', default=''),
        port=dict(type='int', default=0),
        # local disk options
        controller_slot=dict(type='str', default=''),
        bootloader_name=dict(type='str', default=''),
        bootloader_description=dict(type='str', default=''),
        bootloader_path=dict(type='str', default=''),
        # virtual media options
        virtual_media_subtype=dict(
            type='str',
            choices=[
                'None',
                'cimc-mapped-dvd',
                'cimc-mapped-hdd',
                'kvm-mapped-dvd',
                'kvm-mapped-hdd',
                'kvm-mapped-fdd'
            ],
            default='None',
        ),
    )
    argument_spec = intersight_argument_spec
    argument_spec.update(
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        organization=dict(type='str', default='default'),
        name=dict(type='str', required=True),
        description=dict(type='str', aliases=['descr'], default=''),
        tags=dict(type='list', default=[]),
        configured_boot_mode=dict(type='str', choices=['Legacy', 'Uefi'], default='Legacy'),
        uefi_enable_secure_boot=dict(type='bool', default=False),
        boot_devices=dict(type='list', elements='dict', options=boot_device),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )

    intersight = IntersightModule(module)
    intersight.result['api_response'] = {}
    intersight.result['trace_id'] = ''
    #
    # Argument spec above, resource path, and API body should be the only code changed in each policy module
    #
    # Resource path used to configure policy
    resource_path = '/boot/PrecisionPolicies'
    # Defined API body used in compares or create
    intersight.api_body = {
        'Organization': {
            'Name': intersight.module.params['organization'],
        },
        'Name': intersight.module.params['name'],
        'Tags': intersight.module.params['tags'],
        'Description': intersight.module.params['description'],
        'ConfiguredBootMode': intersight.module.params['configured_boot_mode'],
        "EnforceUefiSecureBoot": intersight.module.params['uefi_enable_secure_boot'],
        'BootDevices': [],
    }
    if intersight.module.params.get('boot_devices'):
        for device in intersight.module.params['boot_devices']:
            if device['device_type'] == 'iscsi':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.Iscsi",
                        "ObjectType": "boot.Iscsi",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "Slot": device['network_slot'],
                        "Port": device['port'],
                    }
                )
            elif device['device_type'] == 'local_cdd':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.LocalCDD",
                        "ObjectType": "boot.LocalCDD",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                    }
                )
            elif device['device_type'] == 'local_disk':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.LocalDisk",
                        "ObjectType": "boot.LocalDisk",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "Slot": device['controller_slot'],
                        "Bootloader": {
                            "ClassId": "boot.Bootloader",
                            "ObjectType": "boot.Bootloader",
                            "Description": device['bootloader_description'],
                            "Name": device['bootloader_name'],
                            "Path": device['bootloader_path'],
                        },
                    }
                )
            elif device['device_type'] == 'nvme':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.NVMe",
                        "ObjectType": "boot.NVMe",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "Bootloader": {
                            "ClassId": "boot.Bootloader",
                            "ObjectType": "boot.Bootloader",
                            "Description": device['bootloader_description'],
                            "Name": device['bootloader_name'],
                            "Path": device['bootloader_path'],
                        },
                    }
                )
            elif device['device_type'] == 'pch_storage':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.PchStorage",
                        "ObjectType": "boot.PchStorage",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "Bootloader": {
                            "ClassId": "boot.Bootloader",
                            "ObjectType": "boot.Bootloader",
                            "Description": device['bootloader_description'],
                            "Name": device['bootloader_name'],
                            "Path": device['bootloader_path'],
                        },
                        "Lun": device['lun'],
                    }
                )
            elif device['device_type'] == 'pxe':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.Pxe",
                        "ObjectType": "boot.Pxe",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "IpType": device['ip_type'],
                        "InterfaceSource": device['interface_source'],
                        "Slot": device['network_slot'],
                        "InterfaceName": device['interface_name'],
                        "Port": device['port'],
                        "MacAddress": device['mac_address'],
                    }
                )
            elif device['device_type'] == 'san':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.San",
                        "ObjectType": "boot.San",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "Lun": device['lun'],
                        "Slot": device['network_slot'],
                        "Bootloader": {
                            "ClassId": "boot.Bootloader",
                            "ObjectType": "boot.Bootloader",
                            "Description": device['bootloader_description'],
                            "Name": device['bootloader_name'],
                            "Path": device['bootloader_path'],
                        },
                    }
                )
            elif device['device_type'] == 'sd_card':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.SdCard",
                        "ObjectType": "boot.SdCard",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "Lun": device['lun'],
                        "SubType": device['sd_card_subtype'],
                        "Bootloader": {
                            "ClassId": "boot.Bootloader",
                            "ObjectType": "boot.Bootloader",
                            "Description": device['bootloader_description'],
                            "Name": device['bootloader_name'],
                            "Path": device['bootloader_path'],
                        },
                    }
                )
            elif device['device_type'] == 'uefi_shell':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.UefiShell",
                        "ObjectType": "boot.UefiShell",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                    }
                )
            elif device['device_type'] == 'usb':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.Usb",
                        "ObjectType": "boot.Usb",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "SubType": device['subtype'],
                    }
                )
            elif device['device_type'] == 'virtual_media':
                intersight.api_body['BootDevices'].append(
                    {
                        "ClassId": "boot.VirtualMedia",
                        "ObjectType": "boot.VirtualMedia",
                        "Enabled": device['enabled'],
                        "Name": device['device_name'],
                        "SubType": device['virtual_media_subtype'],
                    }
                )
    #
    # Code below should be common across all policy modules
    #
    # intersight.configure_policy(...)
    organization_moid = None
    # GET Organization Moid
    intersight.get_resource(
        resource_path='/organization/Organizations',
        query_params={
            '$filter': "Name eq '" + intersight.module.params['organization'] + "'",
            '$select': 'Moid',
        },
    )
    if intersight.result['api_response'].get('Moid'):
        # resource exists and moid was returned
        organization_moid = intersight.result['api_response']['Moid']

    intersight.result['api_response'] = {}
    # get the current state of the resource
    filter_str = "Name eq '" + intersight.module.params['name'] + "'"
    filter_str += "and Organization.Moid eq '" + organization_moid + "'"
    intersight.get_resource(
        resource_path=resource_path,
        query_params={
            '$filter': filter_str,
            '$expand': 'Organization',
        },
    )

    moid = None
    resource_values_match = False
    if intersight.result['api_response'].get('Moid'):
        # resource exists and moid was returned
        moid = intersight.result['api_response']['Moid']
        if module.params['state'] == 'present':
            resource_values_match = compare_values(intersight.api_body, intersight.result['api_response'])
        else:  # state == 'absent'
            intersight.delete_resource(
                moid=moid,
                resource_path=resource_path,
            )
            moid = None

    if module.params['state'] == 'present' and not resource_values_match:
        # remove read-only Organization key
        intersight.api_body.pop('Organization')
        if not moid:
            # Organization must be set, but can't be changed after initial POST
            intersight.api_body['Organization'] = {
                'Moid': organization_moid,
            }
        intersight.configure_resource(
            moid=moid,
            resource_path=resource_path,
            body=intersight.api_body,
            query_params={
                '$filter': filter_str,
            },
        )

    module.exit_json(**intersight.result)


if __name__ == '__main__':
    main()
