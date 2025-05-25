// webpack.config.js
const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        main: './src/index.js',
        CameraWorker: './src/CameraWorker.js'
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].js' // [name] will be replaced by the entry key
    }
};