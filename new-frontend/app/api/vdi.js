import axios from 'axios'
export const vdilist = async (page, sizePerPage) =>
{
  return await axios.get('/api/vdilist', {page: page, page_size: sizePerPage});
};

