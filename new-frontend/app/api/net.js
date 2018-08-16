import axios from 'axios'

export const netlist = async (page, sizePerPage) =>
{
  return await axios.get('/api/netlist', {page: page, page_size: sizePerPage});
};

export const netaction = async(vm, net, action) =>
{
  return await axios.post('/api/netaction', {uuid: vm, net, action});
};
