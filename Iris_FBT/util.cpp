#include "util.h"
#include <stdexcept>
#include <Windows.h>
#include <shlobj_core.h>
#include <sstream>

namespace IrisFBT {
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

    std::wstring getDriverPath() {
        wchar_t path[MAX_PATH];
        HMODULE hm = NULL;

        if (GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
            GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
            (LPCWSTR)&getDriverPath, &hm) == 0)
        {
            int ret = GetLastError();
            fprintf(stderr, "GetModuleHandle failed, error = %d\n", ret);
            return std::wstring();
        }
        if (GetModuleFileName(hm, path, sizeof(path)) == 0)
        {
            int ret = GetLastError();
            fprintf(stderr, "GetModuleFileName failed, error = %d\n", ret);
            return std::wstring();
        }

        std::wstring pathstr = std::wstring(path);

        size_t ind = pathstr.rfind(L"/bin/");
        if (ind == std::wstring::npos) {
            ind = pathstr.rfind(L"\\bin\\");
        }
        if (ind == std::wstring::npos) {
            return std::wstring();
        }

        return pathstr.substr(0, ind + 1);
    }


    vector<string> split(const string& text, char delimiter) {
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

}