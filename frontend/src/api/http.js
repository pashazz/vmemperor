var status = function(response) {
    if (response.status >= 200 && response.status < 300) {
      return Promise.resolve(response);
    } else {
      return Promise.reject(new Error(response.statusText));
    }
  },
  json = function(response) {
    return response.json()
  };

var HTTP = {
  
  get: function(url) {
    return fetch(url)
      .then(status)
      .then(json);
  },

  post: function(url, form) {
    return fetch(url, {
        method: 'post',
        body: JSON.stringify(form)
      })
      .then(status)
      .then(json);
  }
};

module.exports = HTTP;