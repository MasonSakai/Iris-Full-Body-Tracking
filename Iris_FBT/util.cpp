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
        }
    }

    static inline double SIGN(double x) {
        return (x >= 0.0f) ? +1.0f : -1.0f;
    }

    static inline double NORM(double a, double b, double c, double d) {
        return sqrt(a * a + b * b + c * c + d * d);
    }

    vr::HmdQuaternion_t mRot2Quat(vector<vector<double>> m) {
        float r11 = m[0][0];
        float r12 = m[0][1];
        float r13 = m[0][2];
        float r21 = m[1][0];
        float r22 = m[1][1];
        float r23 = m[1][2];
        float r31 = m[2][0];
        float r32 = m[2][1];
        float r33 = m[2][2];
        float q0 = (r11 + r22 + r33 + 1.0f) / 4.0f;
        float q1 = (r11 - r22 - r33 + 1.0f) / 4.0f;
        float q2 = (-r11 + r22 - r33 + 1.0f) / 4.0f;
        float q3 = (-r11 - r22 + r33 + 1.0f) / 4.0f;
        if (q0 < 0.0f) {
            q0 = 0.0f;
        }
        if (q1 < 0.0f) {
            q1 = 0.0f;
        }
        if (q2 < 0.0f) {
            q2 = 0.0f;
        }
        if (q3 < 0.0f) {
            q3 = 0.0f;
        }
        q0 = sqrt(q0);
        q1 = sqrt(q1);
        q2 = sqrt(q2);
        q3 = sqrt(q3);
        if (q0 >= q1 && q0 >= q2 && q0 >= q3) {
            q0 *= +1.0f;
            q1 *= SIGN(r32 - r23);
            q2 *= SIGN(r13 - r31);
            q3 *= SIGN(r21 - r12);
        }
        else if (q1 >= q0 && q1 >= q2 && q1 >= q3) {
            q0 *= SIGN(r32 - r23);
            q1 *= +1.0f;
            q2 *= SIGN(r21 + r12);
            q3 *= SIGN(r13 + r31);
        }
        else if (q2 >= q0 && q2 >= q1 && q2 >= q3) {
            q0 *= SIGN(r13 - r31);
            q1 *= SIGN(r21 + r12);
            q2 *= +1.0f;
            q3 *= SIGN(r32 + r23);
        }
        else if (q3 >= q0 && q3 >= q1 && q3 >= q2) {
            q0 *= SIGN(r21 - r12);
            q1 *= SIGN(r31 + r13);
            q2 *= SIGN(r32 + r23);
            q3 *= +1.0f;
        }
        else {
            printf("coding error\n");
        }
        float r = NORM(q0, q1, q2, q3);
        q0 /= r;
        q1 /= r;
        q2 /= r;
        q3 /= r;

        return vr::HmdQuaternion_t{ q0, q1, q2, q3 };
    }
}