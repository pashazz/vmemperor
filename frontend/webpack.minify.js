var path = require('path');
var webpack = require("webpack");

module.exports = {
  entry: path.resolve(__dirname, 'src/app.jsx'),
  output: {
    path: path.resolve(__dirname, '../static/js'),
    filename: 'bundle.js'
  },

  module: {
    loaders: [
      {
        test: /src\/.+.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel'
      }
    ]
  },

  plugins: [
    new webpack.optimize.UglifyJsPlugin({minimize: true})
  ]
};
