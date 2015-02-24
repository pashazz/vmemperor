var VM = function(object) {
  this.id = object['uuid'];
  this.name = object['name_label'];
  this.pool = 'A';
  this.endpoint_url = object['endpoint']['url'];
  this.endpoint_description = object['endpoint']['description'];
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