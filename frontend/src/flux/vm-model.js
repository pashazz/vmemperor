// POJO from  
// {  
//    "VCPUs_at_startup":"1",
//    "allowed_operations":[  
//       "changing_dynamic_range",
//       "migrate_send",
//       "pool_migrate",
//       "changing_VCPUs_live",
//       "suspend",
//       "hard_reboot",
//       "hard_shutdown",
//       "clean_reboot",
//       "clean_shutdown",
//       "pause",
//       "checkpoint",
//       "snapshot"
//    ],
//    "endpoint":{  
//       "url":"https://172.31.0.14:443/",
//       "description":"Pool A"
//    },
//    "guest_metrics":"OpaqueRef:be184b05-d3bd-0887-cd3a-ff77887da5da",
//    "is_a_snapshot":false,
//    "is_a_template":false,
//    "is_control_domain":false,
//    "memory_dynamic_max":"1610612736",
//    "memory_dynamic_min":"268435456",
//    "memory_target":"1610612736",
//    "name_description":"Installed via xe CLI",
//    "name_label":"sentanal",
//    "networks":{  
//       "0/ip":"172.31.167.66",
//       "0/ipv6/0":"fe80::b0c9:5bff:fe1f:5896"
//    },
//    "power_state":"Running",
//    "uuid":"6a302da8-80a1-f795-950c-e2025a2cf530"
// }

var VM = function(object) {
  this.id = object['uuid'];
  this.name = object['name_label'];
  this.endpoint_url = object['endpoint']['url'];
  this.endpoint_description = this.pool = object['endpoint']['description'];
  this.description = object['name_description'] || '';
  if(object['networks']) {
    this.ip = object['networks']['0/ip'] || '';  
  } else {
    this.ip = '';  
  }

  
  this.vcpus = parseInt(object['VCPUs_at_startup']) || 0;
  this.RAM = 'hard =(';
  this.state = object['power_state'] || '';
} 

module.exports = VM;