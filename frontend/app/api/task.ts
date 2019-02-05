import axios from "axios";

export interface Task
{
  task: string,
}


export const taskstatus = async (task: string) => {
  return await axios.post('/api/taskstatus', {task});
};
