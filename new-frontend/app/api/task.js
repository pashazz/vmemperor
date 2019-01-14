import axios from "axios";

export const taskstatus = async (task) => {
  return await axios.post('/api/taskstatus', {task});
};
