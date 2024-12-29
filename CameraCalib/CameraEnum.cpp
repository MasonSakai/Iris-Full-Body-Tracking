#include "CameraEnum.h"
#include <comdef.h>
#include <windows.h>
#include <dshow.h>
#include <iostream>

#pragma comment(lib, "strmiids")

vector<CameraEnum>* CameraDescriptors = NULL;

string BstrToString(BSTR bstr) {
    if (!bstr) {
        return "";
    }

    _bstr_t wrapper(bstr, false); // false to avoid making a copy
    return string((char*)wrapper);
}

HRESULT EnumerateDevices(REFGUID category, IEnumMoniker** ppEnum)
{
    // Create the System Device Enumerator.
    ICreateDevEnum* pDevEnum;
    HRESULT hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL,
        CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pDevEnum));

    if (SUCCEEDED(hr))
    {
        // Create an enumerator for the category.
        hr = pDevEnum->CreateClassEnumerator(category, ppEnum, 0);
        if (hr == S_FALSE)
        {
            hr = VFW_E_NOT_FOUND;  // The category is empty. Treat as an error.
        }
        pDevEnum->Release();
    }
    return hr;
}


void GetDeviceInformation(IEnumMoniker* pEnum)
{
    if (CameraDescriptors == NULL) {
        CameraDescriptors = new vector<CameraEnum>();
    }
    else CameraDescriptors->clear();

    IMoniker* pMoniker = NULL;

    while (pEnum->Next(1, &pMoniker, NULL) == S_OK)
    {
        IPropertyBag* pPropBag;
        HRESULT hr = pMoniker->BindToStorage(0, 0, IID_PPV_ARGS(&pPropBag));
        if (FAILED(hr))
        {
            pMoniker->Release();
            continue;
        }

        VARIANT var;
        VariantInit(&var);

        CameraEnum cam;

        // Get description or friendly name.
        hr = pPropBag->Read(L"Description", &var, 0);
        if (FAILED(hr))
        {
            hr = pPropBag->Read(L"FriendlyName", &var, 0);
        }
        if (SUCCEEDED(hr))
        {
            cam.description = BstrToString(var.bstrVal);
            VariantClear(&var);
        }

        //hr = pPropBag->Write(L"FriendlyName", &var);

        hr = pPropBag->Read(L"DevicePath", &var, 0);
        if (SUCCEEDED(hr))
        {
            // The device path is not intended for display.
            cam.devicePath = BstrToString(var.bstrVal);
            VariantClear(&var);
        }

        CameraDescriptors->push_back(cam);
        pPropBag->Release();
        pMoniker->Release();
    }
}
void DisplayDeviceInformation()
{
    for (int i = 0; i < CameraDescriptors->size(); i++) {
        cout << i << ": " << CameraDescriptors->at(i).description << " - " << CameraDescriptors->at(i).devicePath << endl;
    }
}

vector<CameraEnum>* GetCams()
{
    HRESULT hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);
    if (SUCCEEDED(hr))
    {
        IEnumMoniker* pEnum;

        hr = EnumerateDevices(CLSID_VideoInputDeviceCategory, &pEnum);
        if (SUCCEEDED(hr))
        {
            GetDeviceInformation(pEnum);
            pEnum->Release();
        }
        CoUninitialize();
        //DisplayDeviceInformation();
    }

    return CameraDescriptors;
}