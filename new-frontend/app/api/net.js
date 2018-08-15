import axios from 'axios'

export const netlist = async (page, sizePerPage) =>
{
  return await axios.get('/api/netlist', {page: page, page_size: sizePerPage});
};


