var debug = process.env.NODE_ENV !== "production";
var path = require("path");
var webpack = require("webpack");

var ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
  context: __dirname,
  devtool: debug ? "inline-sourcemap" : null,
  entry: "./build/main.js",
  output: {
    path: __dirname + "/app/static",
    filename: "bundle.min.js"
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /(node_modules|bower_components)/,
        loader: "babel-loader",
        query: {
          presets: ["es2015", "react", "stage-0"],
          plugins: ["react-html-attrs", "transform-class-properties", "transform-decorators-legacy"]
        }
      },
      {
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract("css!sass")
      }
    ]
  },
  plugins: debug ? [
    new ExtractTextPlugin("styles.css", {allChunks: true})
  ] : [
    new ExtractTextPlugin("styles.css", {allChunks: true}),
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.OccurenceOrderPlugin(),
    new webpack.optimize.UglifyJsPlugin({ mangle: false, sourcemap: false }),
  ]
};
