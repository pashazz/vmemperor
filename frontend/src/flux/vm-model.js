var VM = function(object) {
  this.id = object['uuid'];
  this.name = object['name_label'];
  this.ip = object['networks']['0/ip'];
  this.vcpus = parseInt(object['VCPUs_at_startup']);
  this.RAM = 'hard =(';
  this.state = object['power_state'];
} 

module.exports = VM;