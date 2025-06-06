#pragma once
#include <vector>
#include <string>

using std::wstring;
using std::string;
using std::vector;

wstring getAppdata();
vector<string> string_split(const string& text, char delimiter);

