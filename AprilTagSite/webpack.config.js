// webpack.config.js
const path = require('path');

base_exp = {
    mode: 'development',
    entry: {
        apriltag: './build/apriltag.js',
    },
    resolve: {
        alias: {
            '@app': path.resolve(__dirname, 'build/')
        },
        extensions: [".tsx", ".ts", ".js"]
    },
    externals: {
        bootstrap: 'bootstrap'
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
        path: path.resolve(__dirname, '../IrisCore/app/apriltag/static/js'),
        filename: '[name].js' // [name] will be replaced by the entry key
    }
}

module.exports = [dist_exp, core_exp];