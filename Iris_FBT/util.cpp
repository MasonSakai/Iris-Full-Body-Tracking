#include "util.h"
#include <stdexcept>
#include <Windows.h>
#include <shlobj_core.h>
#include <sstream>
using msg_ptr = sio::message::ptr;

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

    json messageToJson(msg_ptr ptr) {
        switch (ptr->get_flag()) {
        case sio::message::flag_integer:
            return ptr->get_int();
        case sio::message::flag_double:
            return ptr->get_double();
        case sio::message::flag_string:
            return ptr->get_string();
        case sio::message::flag_boolean:
            return ptr->get_bool();
        case sio::message::flag_binary: {
            const std::shared_ptr<const string>& bin = ptr->get_binary();
            return json::binary(std::vector<uint8_t>(bin->begin(), bin->end()));
        }
        case sio::message::flag_null:
            return json();
        case sio::message::flag_array: {
            std::vector<msg_ptr> data = ptr->get_vector();
            json::array_t arr = json::array();
            arr.reserve(data.size());
            std::transform(data.begin(), data.end(), std::back_inserter(arr), messageToJson);
            return arr;
        }
        case sio::message::flag_object: {
            std::map<string, msg_ptr> data = ptr->get_map();
            json::object_t obj = json::object();
            std::transform(data.begin(), data.end(), std::inserter(obj, obj.begin()),
                [](const std::pair<string, msg_ptr>& p) {
                    return std::make_pair(p.first, messageToJson(p.second));
                });
            return obj;
        }
        default:
            return nullptr;
        }
    }
    
    
}