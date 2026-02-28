// webpack.config.js
const path = require('path');

base_exp = {
    mode: 'production',
    entry: {
        camwin: './build/camwin.js',
    }
}

dist_exp = {
    ...base_exp,
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].js' // [name] will be replaced by the entry key
    }
}

core_exp = {
    ...base_exp,
    output: {
        path: path.resolve(__dirname, '../IrisCore/app/cameras/static/js'),
        filename: '[name].js' // [name] will be replaced by the entry key
    }
}

module.exports = [dist_exp, core_exp];