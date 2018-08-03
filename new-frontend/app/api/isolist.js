import axios from 'axios'
const isolist = async (page, sizePerPage) =>
{
  return await axios.get('/api/isolist', {page, sizePerPage});
};

export default isolist;
