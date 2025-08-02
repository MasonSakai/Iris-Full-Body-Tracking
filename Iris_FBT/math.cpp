#include "math.h"

namespace IrisFBT {
    vr::HmdQuaternion_t mRot2Quat(Mat4x4 m) {
        vr::HmdQuaternion_t q{ };

        q.w = sqrt(fmax(0, 1 + m.m[0][0] + m.m[1][1] + m.m[2][2])) / 2;
        q.x = sqrt(fmax(0, 1 + m.m[0][0] - m.m[1][1] - m.m[2][2])) / 2;
        q.y = sqrt(fmax(0, 1 - m.m[0][0] + m.m[1][1] - m.m[2][2])) / 2;
        q.z = sqrt(fmax(0, 1 - m.m[0][0] - m.m[1][1] + m.m[2][2])) / 2;

        q.x = copysign(q.x, m.m[2][1] - m.m[1][2]);
        q.y = copysign(q.y, m.m[0][2] - m.m[2][0]);
        q.z = copysign(q.z, m.m[1][0] - m.m[0][1]);

        return q;
    }

    Vector3::Vector3() : v{ 0, 0, 0 } {}
    Vector3::Vector3(double x, double y, double z) : v{ x, y, z } {}
    Vector3::Vector3(json& data)
    {
        for (int i = 0; i < 3; ++i) { // Row of result matrix
            v[i] = data[i][3].get<double>();
        }
    }
    Vector3::Vector3(vr::HmdMatrix34_t & mat) : v{ mat.m[0][3], mat.m[1][3], mat.m[2][3], } {}
    Vector3 Vector3::operator*(double d) const {
        return Vector3(v[0] * d, v[1] * d, v[2] * d);
    }
    Vector3 Vector3::operator/(double d) const
    {
        return Vector3(v[0] / d, v[1] / d, v[2] / d);
    }
    Vector3 Vector3::operator+(const Vector3 a) const
    {
        return Vector3(v[0] + a.v[0], v[1] + a.v[1], v[2] + a.v[2]);
    }
    Vector3 Vector3::operator-(const Vector3 a) const
    {
        return Vector3(v[0] - a.v[0], v[1] - a.v[1], v[2] - a.v[2]);
    }
    double Vector3::operator*(const Vector3 a) const {
        return v[0] * a.v[0] + v[1] * a.v[1] + v[2] * a.v[2];
    }
    double Vector3::length() const {
        return sqrt(*this * *this);
    }


    Mat4x4::Mat4x4() {

        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                m[i][j] = i == j;
            }
        }
    }
    Mat4x4::Mat4x4(json& data) {
        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                m[i][j] = data[i][j].get<double>();
            }
        }
    }
    Mat4x4 Mat4x4::operator*(const Mat4x4 a) const
    {
        Mat4x4 res{};
        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                for (int k = 0; k < 4; ++k) { // Elements for dot product
                    res.m[i][j] += this->m[i][k] * a.m[k][j];
                }
            }
        }
        return res;
    }
    Vector3 Mat4x4::operator*(const Vector3 a) const
    {
        Vector3 res;
        for (int i = 0; i < 3; i++) {
            for (int k = 0; k < 3; ++k) {
                res.v[i] += this->m[i][k] * a.v[k];
            }
            res.v[i] += this->m[i][3];
        }
        return res;
    }
}