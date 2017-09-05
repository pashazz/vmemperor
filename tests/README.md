This directory contains VMEmperor tests.
These tests require the following settings (files to be placed in this directory):

* `test_ldap_login`: ISP RAS LDAP login test - file `secret,ini`
  ```
  [test]
  username = ISP RAS username
  password = ISP RAS password
  ```

* `test_createvm`: Test Xen VM creation - file `createvm.ini`
  This file contains multiple sections with different names.
  Each section specifies one test VM configuration.
  Example :
  ```
  [section]
  name_label: VM Name
  template = template UUID
  storage = SR UUID
  network = VIF UUID
  vdi_size = disk image size in bytes
  hostname = VM hostname
  os_kind = OS type (currently only 'ubuntu')
  fullname = user's full name
  username = user's UNIX username
  password = user's UNIX password
  mirror_url = repository mirror host
  mirror_path = repository mirror path (w/o host)
