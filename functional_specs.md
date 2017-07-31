# VMEmperor functional specs

VMEmperor is a system for automated creation of virtual machines in Xen environment under XAPI management.

The system should be able to do the following.

## The system should be able to manage multiple Xen pools concurrently

List of hosts and pools used by VMEmperor should be defined in system settings. Sensitive admin credentials should be stored in separate protected (encrypted) files or plain-text files (defined by user-choice).

## Provide separate root-level and user-level pluggable login system

Root-level auth should be separate from user-level auth. User-level login subsystem should be implemented in pluggable way with intermediate interface that this subsystem should provide.
Optional (in near future): per-user granulated resource quotas + group-granulated resource quotas.
Optional (in far future): fail2ban module for hacking defense.

## Let users manage existing virtual machines

Each user should be able to:

1. Start
2. Stop
3. Delete (should be turnable-off by an option in config)
4. View info
5. Attach additional disks (should be turnable-off by an option in config)
6. View the desktop through VNC-proxy

## Show information about pool resources

Users and admins should see different pool info. In general admins should see sensitive info (like addresses, full template list, full VMs list) and users should not.

## Provide automated net-install procedures for rhel-like and debian-like OS

VMEmperor should provide a basic HTTP-server that provide net-install procedures for automated OS installation using templating systems over *preseed* and *kickstart* installation instructions. Basically we should support CentOS 6-7 and Ubuntu-server deploiments 12.04-16.04 versions.

## Provide VNC-proxy functionality for VM control and manual OS install in-browser

The system should provide VNC-proxy with HTML5 VNC web-view for VMs installation and control.

## Provide a choice between PV and HVM modes for VMs

The system should provide options for creating PV and HVM virtual machines by administrator choice. The choice should be done on tempalates config stage.

## Automated install of guest-utilities for guest VMs

Guest-utils should be installed during the system installation since it's the only way to know machines actual IP addresses after OS installation process.

## The system should store history of user-actions

All the actions should be logged somehow.

## The system should provide Sentry integration

Sentry location should be configurable via VMEmperor config. It should be an optional feature.

https://docs.sentry.io/clients/python/integrations/tornado/

## The system should store settings of creation for VMs (enabled with an option)

It should be an optional feature in VMEmperor config.

## Provide network configuration for virtual machines

System should provide an ability to choose network to use. Also network configuration should provide automatic mode (dhcp) or static config.

Administrator should be able to shadow specific networks for users (like management network) via web-interface.

## Provide plugin-like post-creation hooks via Ansible

The system should provide an ability to write some kind of manifest (description, input parameters, subject for action) and ansible scenarios to use. These scenarios should be read by the system on system start and should be shown to system administrators. Administrator should be able to set these scenarios for OS templates as "available for usage", "activated always" or "disabled" in user-interface. Admin should be able to set default parameters values (as a hint for users) per-template. Just in case: templates themselves are pool-specific, so it's ok.

## Provide easy templates configuration

Admin should be able to set up mirror for net-install and some basic parameters for VM automated creation (like PV or HVM mode). Admin can mark a template as a template for manual interactive installation.

## The system should store minimum information in itself

Info about templates, shadowed nets, users-to-VMs correspondance should be stored via Xen tags in Xenserver pools themselves.

## The system should provide live notifications and events via websockets

At least for creation status and VM states. The data should be collected via XAPI in some intervals but pushed to users in stream-like mode.