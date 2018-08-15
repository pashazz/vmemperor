import axios from 'axios'
export const vdilist = async (page, sizePerPage) =>
{
  return await axios.get('/api/vdilist', {page: page, page_size: sizePerPage});
};

export const attachdetachvdi = async(vm, vdi, action)  =>
{
  console.log("in detachvdi");
  return await  axios.post('/api/attachdetachvdi', {uuid: vm, vdi: vdi,
  action});
};

export const attachdetachiso = async(vm, iso, action) =>
{
  console.log("in attachiso");
  return await  axios.post('/api/attachdetachiso', {uuid: vm, iso: iso,
    action});
};
