// webpack.config.js
const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        apriltag: './src/apriltag.js',
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].js' // [name] will be replaced by the entry key
    }
};