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