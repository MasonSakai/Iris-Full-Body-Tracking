#include "util.h"
#include <Windows.h>
#include <shlobj_core.h>


const wchar_t AppdataDirectory[] = L"/IrisFBT/";

std::wstring getAppdata() {
    std::wstring wstr;
    PWSTR appDataPath = NULL;
    if (SHGetKnownFolderPath(FOLDERID_RoamingAppData, 0, NULL, &appDataPath) == S_OK) {
        wstr = std::wstring(appDataPath) + AppdataDirectory;
    }
    CoTaskMemFree(appDataPath);
    return wstr;
}


vector<string> string_split(const string& text, char delimiter) {
    vector<string> result;
    string::size_type start = 0;
    string::size_type end = text.find(delimiter);

    while (end != string::npos) {
        result.push_back(text.substr(start, end - start));
        start = end + 1;
        end = text.find(delimiter, start);
    }
    result.push_back(text.substr(start));
    return result;
}


Mat LoadMat(json& config) {
    if (config.is_null()) return Mat();

    Mat mat(config["rows"].get<int>(),
            config["cols"].get<int>(),
            config["type"].get<int>());

    for (int r = 0; r < mat.rows; ++r) {
        for (int c = 0; c < mat.cols; ++c) {
            mat.at<double>(r, c) = config["data"][r][c].get<double>();
        }
    }

    return mat;
}
json SaveMat(Mat& mat) {
    json config = json::object();
    config["rows"] = mat.rows;
    config["cols"] = mat.cols;
    config["type"] = mat.type();

    json j_rows = json::array();
    for (int r = 0; r < mat.rows; ++r) {
        json j_col = json::array();
        for (int c = 0; c < mat.cols; ++c) {
            j_col.push_back(mat.at<double>(r, c));
        }
        j_rows.push_back(j_col);
    }
    config["data"] = j_rows;

    return config;
}