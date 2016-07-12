// POJO from
// {
//   "url": "http://172.31.0.14:80/",
//   "description": "Pool A",
//   "host_list": [
//     {
//       "memory_free": 9,
//       "software_version": {
//         "linux": "3.10.0+2",
//         "platform_version": "1.9.0",
//         "hostname": "squeeze-1",
//         "build_number": "90233c",
//         "xcp:main": "Base Pack, version 1.9.0, build 90233c",
//         "xs:xenserver-transfer-vm": "XenServer Transfer VM, version 6.5.0, build 90158c",
//         "network_backend": "openvswitch",
//         "xen": "4.4.1-xs100654",
//         "product_version": "6.5.0",
//         "xapi": "1.3",
//         "platform_name": "XCP",
//         "product_brand": "XenServer",
//         "xencenter_max": "2.4",
//         "product_version_text_short": "6.5",
//         "date": "2015-04-17",
//         "product_version_text": "6.5",
//         "xs:main": "XenServer Pack, version 6.5.0, build 90233c",
//         "xencenter_min": "2.3",
//         "dbv": "2015.0101"
//       },
//       "name_label": "b",
//       "memory_available": 27590,
//       "memory_total": 32718,
//       "cpu_info": {
//         "physical_features": "77bae3ff-bfebfbff-00000001-28100800",
//         "modelname": "Intel(R) Core(TM) i7-3770 CPU @ 3.40GHz",
//         "vendor": "GenuineIntel",
//         "features": "77bae3ff-bfebfbff-00000001-28100800",
//         "family": "6",
//         "maskable": "full",
//         "cpu_count": "8",
//         "socket_count": "1",
//         "flags": "fpu de tsc msr pae mce cx8 apic sep mca cmov pat clflush acpi mmx fxsr sse sse2 ss ht syscall nx lm constant_tsc rep_good nopl nonstop_tsc pni pclmulqdq monitor vmx est ssse3 cx16 sse4_1 sse4_2 popcnt tsc_deadline_timer aes f16c rdrand hypervisor lahf_lm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase erms",
//         "stepping": "9",
//         "model": "58",
//         "features_after_reboot": "77bae3ff-bfebfbff-00000001-28100800",
//         "speed": "3392.388"
//       },
//       "live": true,
//       "resident_VMs": [
//         "OpaqueRef:75647f3b-339d-c5a5-31cd-23ce60f56f24",
//         "OpaqueRef:6ac42719-cfdd-b8d0-c54a-5e62fea11031",
//         "OpaqueRef:4490950a-30b7-ce31-aad0-a4f38f4f6001",
//         "OpaqueRef:46a35c9c-3e53-a199-eec4-e44ce15bbbed",
//         "OpaqueRef:670330ee-42c0-36a3-6261-b5abe217f1ee",
//         "OpaqueRef:dd410bbc-0029-b0ab-15d7-577e5dc06774",
//         "OpaqueRef:782bf931-edb6-a71d-2082-fb440c7c8fd2"
//       ]
//     }
//   ],
//   "hdd_available": 5729,
//   "id": "sadasdasdasdas"
// }

export default function Pool(object) {
  this.id = object['id'];
  this.url = object['url'];
  this.description = object['description'];

  this.host_list = object['host_list'];

  this.hdd_available = object['hdd_available']
}
