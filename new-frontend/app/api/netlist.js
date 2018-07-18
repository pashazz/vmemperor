import axios from 'axios'
const netlist = async () =>
{
  return await axios.get('api/netlist');
};

export default netlist;
