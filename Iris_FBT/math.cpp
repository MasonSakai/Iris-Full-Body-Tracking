#include "math.h"
#include <cmath>
#include <limits>

namespace IrisFBT {
    Vector3::Vector3() : v{0, 0, 0} {}
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
    Vector3 Vector3::operator*=(double d)
    {
        v[0] *= d;
        v[1] *= d;
        v[2] *= d;
        return *this;
    }
    Vector3 Vector3::operator/(double d) const
    {
        return Vector3(v[0] / d, v[1] / d, v[2] / d);
    }
    Vector3 Vector3::operator/=(double d)
    {
        v[0] /= d;
        v[1] /= d;
        v[2] /= d;
        return *this;
    }
    Vector3 Vector3::operator+(const Vector3 a) const
    {
        return Vector3(v[0] + a.v[0], v[1] + a.v[1], v[2] + a.v[2]);
    }
    Vector3 Vector3::operator+=(const Vector3 a)
    {
        v[0] += a.v[0];
        v[1] += a.v[1];
        v[2] += a.v[2];
        return *this;
    }
    Vector3 Vector3::operator-(const Vector3 a) const
    {
        return Vector3(v[0] - a.v[0], v[1] - a.v[1], v[2] - a.v[2]);
    }
    Vector3 Vector3::operator-() const
    {
        return Vector3(-v[0], -v[1], -v[2]);
    }
    Vector3 Vector3::operator-=(const Vector3 a)
    {
        v[0] -= a.v[0];
        v[1] -= a.v[1];
        v[2] -= a.v[2];
        return *this;
    }
    double Vector3::operator*(const Vector3 a) const {
        return dot(*this, a);
    }
    double Vector3::dot(const Vector3 a, const Vector3 b)
    {
        return a.v[0] * b.v[0] + a.v[1] * b.v[1] + a.v[2] * b.v[2];
    }
    Vector3 Vector3::cross(const Vector3 a, const Vector3 b)
    {
        return Vector3(a.v[1] * b.v[2] - a.v[2] * b.v[1],
                       a.v[2] * b.v[0] - a.v[0] * b.v[2],
                       a.v[0] * b.v[1] - a.v[1] * b.v[0]);
    }
    Vector3 Vector3::project(const Vector3 a, const Vector3 b)
    {
        return b * (dot(a, b) / dot(b, b));
    }
    Vector3 Vector3::reject(const Vector3 a, const Vector3 b)
    {
        return a - project(a, b);
    }
    Vector3 Vector3::normalized() const
    {
        return *this / length();
    }
    double Vector3::length() const {
        return sqrt(dot(*this, *this));
    }
    string Vector3::to_string() const
    {
        return '(' + std::to_string(v[0]) + ", " + std::to_string(v[1]) + ", " + std::to_string(v[2]) + ')';
    }

    Mat3x3::Mat3x3() {

        for (int i = 0; i < 3; ++i) { // Row of result matrix
            for (int j = 0; j < 3; ++j) { // Column of result matrix
                m[i][j] = i == j;
            }
        }
    }
    Mat3x3::Mat3x3(int) : m{ 0 } {}
    Mat3x3::Mat3x3(json& data) {
        for (int i = 0; i < 3; ++i) { // Row of result matrix
            for (int j = 0; j < 3; ++j) { // Column of result matrix
                m[i][j] = data[i][j].get<double>();
            }
        }
    }
    Mat3x3::Mat3x3(const Vector3 x, const Vector3 y, const Vector3 z)
    {
        for (int i = 0; i < 3; i++) {
            m[i][0] = x.v[i];
            m[i][1] = y.v[i];
            m[i][2] = z.v[i];
        }
    }
    Mat3x3::Mat3x3(const vr::HmdQuaternion_t q)
    {
        m[0][0] = 1. - 2. * (q.y * q.y + q.z * q.z);
        m[0][1] = 2. * (q.x * q.y - q.z * q.w);
        m[0][2] = 2. * (q.x * q.z + q.y * q.w);

        m[1][0] = 2. * (q.x * q.y + q.z * q.w);
        m[1][1] = 1. - 2. * (q.x * q.x + q.z * q.z);
        m[1][2] = 2. * (q.y * q.z - q.x * q.w);

        m[2][0] = 2. * (q.x * q.z - q.y * q.w);
        m[2][1] = 2. * (q.y * q.z + q.x * q.w);
        m[2][2] = 1. - 2. * (q.x * q.x + q.y * q.y);
    }
    Mat3x3 Mat3x3::operator*(const Mat3x3 a) const
    {
        Mat3x3 res(0);
        for (int i = 0; i < 3; ++i) { // Row of result matrix
            for (int j = 0; j < 3; ++j) { // Column of result matrix
                for (int k = 0; k < 3; ++k) { // Elements for dot product
                    res.m[i][j] += this->m[i][k] * a.m[k][j];
                }
            }
        }
        return res;
    }
    Vector3 Mat3x3::operator*(const Vector3 a) const
    {
        Vector3 res;
        for (int i = 0; i < 3; i++) {
            for (int k = 0; k < 3; ++k) {
                res.v[i] += this->m[i][k] * a.v[k];
            }
        }
        return res;
    }
    Mat3x3 Mat3x3::transpose() const
    {
        Mat3x3 inv;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                inv.m[i][j] = m[j][i];
        return inv;
    }
    double Mat3x3::determinant() const
    {
        return
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
    }
    string Mat3x3::to_string() const
    {
        string str = "[\n";
        for (int i = 0; i < 3; i++) {
            str += " [";
            for (int j = 0; j < 3; j++)
                str += std::to_string(m[i][j]) + ", ";
            str += "]\n";
        }
        return str + ']';
    }

    Mat4x4::Mat4x4() {

        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                m[i][j] = i == j;
            }
        }
    }
    Mat4x4::Mat4x4(int) : m{ 0 } {}
    Mat4x4::Mat4x4(json& data) {
        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                m[i][j] = data[i][j].get<double>();
            }
        }
    }
    Mat4x4::Mat4x4(const Mat3x3 R, const Vector3 p)
    {
        for (int i = 0; i < 3; i++) {
            m[i][0] = R.m[i][0];
            m[i][1] = R.m[i][1];
            m[i][2] = R.m[i][2];
            m[i][3] = p.v[i];
        }
        m[3][0] = 0;
        m[3][1] = 0;
        m[3][2] = 0;
        m[3][3] = 1;
    }
    Mat4x4::Mat4x4(const vr::HmdQuaternion_t q, const Vector3 v)
    {
        m[0][0] = 1. - 2. * (q.y * q.y + q.z * q.z);
        m[0][1] = 2. * (q.x * q.y - q.z * q.w);
        m[0][2] = 2. * (q.x * q.z + q.y * q.w);
        m[0][3] = v.v[0];

        m[1][0] = 2. * (q.x * q.y + q.z * q.w);
        m[1][1] = 1. - 2. * (q.x * q.x + q.z * q.z);
        m[1][2] = 2. * (q.y * q.z - q.x * q.w);
        m[1][3] = v.v[1];

        m[2][0] = 2. * (q.x * q.z - q.y * q.w);
        m[2][1] = 2. * (q.y * q.z + q.x * q.w);
        m[2][2] = 1. - 2. * (q.x * q.x + q.y * q.y);
        m[2][3] = v.v[2];

        m[3][0] = 0;
        m[3][1] = 0;
        m[3][2] = 0;
        m[3][3] = 1;
    }
    Mat4x4 Mat4x4::operator*(const Mat4x4 a) const
    {
        Mat4x4 res(0);
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
    Mat4x4 Mat4x4::inverse() const
    {
        Mat4x4 inv;

        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                inv.m[i][j] = m[j][i];

        Vector3 pos(m[0][3], m[1][3], m[2][3]);
        pos = inv * pos;
        inv.m[0][3] = -pos.v[0];
        inv.m[1][3] = -pos.v[1];
        inv.m[2][3] = -pos.v[2];
        return inv;
    }
    Mat3x3 Mat4x4::get_rotation() const
    {
        Mat3x3 res;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                res.m[i][j] = m[i][j];
        return res;
    }
    Vector3 Mat4x4::get_vector(int i) const
    {
        return Vector3(m[0][i], m[1][i], m[2][i]);
    }
    void Mat4x4::set_vector(const Vector3 v, int i)
    {
        m[0][i] = v.v[0];
        m[1][i] = v.v[1];
        m[2][i] = v.v[2];
    }
    string Mat4x4::to_string() const
    {
        string str = "[\n";
        for (int i = 0; i < 4; i++) {
            str += " [";
            for (int j = 0; j < 4; j++)
                str += std::to_string(m[i][j]) + ", ";
            str += "]\n";
        }
        return str + ']';
    }


    vr::HmdQuaternion_t mRot2Quat(const Mat3x3& m) {
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


    static Vector3 smallestEigenVector(double A[3][3], int maxIter = 50, double tol = 1e-10) {
        // Only works for symmetric 3x3 matrices
        double V[3][3] = {
            {1, 0, 0},
            {0, 1, 0},
            {0, 0, 1}
        };

        for (int iter = 0; iter < maxIter; ++iter) {
            // Find largest off-diagonal element
            int p = 0, q = 1;
            double maxVal = std::fabs(A[0][1]);

            if (std::fabs(A[0][2]) > maxVal) { p = 0; q = 2; maxVal = std::fabs(A[0][2]); }
            if (std::fabs(A[1][2]) > maxVal) { p = 1; q = 2; maxVal = std::fabs(A[1][2]); }

            if (maxVal < tol)
                break;  // Matrix is already diagonal

            // Jacobi rotation
            double theta = 0.5 * (A[q][q] - A[p][p]) / A[p][q];
            double t = (theta == 0.0) ? 1.0 : 1.0 / (std::fabs(theta) + std::sqrt(theta * theta + 1.0));
            if (theta < 0.0) t = -t;

            double c = 1.0 / std::sqrt(t * t + 1.0);
            double s = t * c;

            // Rotate A
            double App = A[p][p];
            double Aqq = A[q][q];
            double Apq = A[p][q];

            A[p][p] = c * c * App - 2.0 * s * c * Apq + s * s * Aqq;
            A[q][q] = s * s * App + 2.0 * s * c * Apq + c * c * Aqq;
            A[p][q] = A[q][p] = 0.0;

            for (int r = 0; r < 3; ++r) {
                if (r != p && r != q) {
                    double Arp = A[r][p];
                    double Arq = A[r][q];
                    A[r][p] = A[p][r] = c * Arp - s * Arq;
                    A[r][q] = A[q][r] = c * Arq + s * Arp;
                }
            }

            // Rotate eigenvector matrix V
            for (int r = 0; r < 3; ++r) {
                double vrp = V[r][p];
                double vrq = V[r][q];
                V[r][p] = c * vrp - s * vrq;
                V[r][q] = s * vrp + c * vrq;
            }
        }

        // Find eigenvector with smallest eigenvalue (diagonal element of A)
        int minIdx = 0;
        double minVal = A[0][0];
        for (int i = 1; i < 3; ++i) {
            if (A[i][i] < minVal) {
                minVal = A[i][i];
                minIdx = i;
            }
        }

        return Vector3(V[0][minIdx], V[1][minIdx], V[2][minIdx]).normalized();
    }

    Vector3 computePlaneNormal(const Vector3 directions[], const int N) {
        if (N < 3) {
            throw std::runtime_error("At least 3 vectors are needed to define a plane");
        }

        // Step 1: Compute the mean vector
        Vector3 mean;
        for (int i = 0; i < N; i++) {
            mean = mean + directions[i];
        }
        mean = mean / N;

        // Step 2: Build covariance matrix (3x3)
        double cov[3][3] = { 0 };

        for (int n = 0; n < N; n++) {
            Vector3 centered = directions[n] - mean;

            for (int i = 0; i < 3; ++i) {
                for (int j = 0; j < 3; ++j) {
                    cov[i][j] += centered.v[i] * centered.v[j];
                }
            }
        }

        // Normalize covariance matrix
        for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j)
                cov[i][j] /= N;

        // Step 3: Compute eigenvectors of the covariance matrix
        // For 3x3 symmetric matrices, you can use the Jacobi method or hardcode an analytical solver.
        // Here we will just sketch it; in production, you'd use a tested SVD/eigen routine.
        //
        // We'll assume a helper function:
        //   Vector3 smallestEigenVector(double cov[3][3])
        // That returns the eigenvector corresponding to the smallest eigenvalue.

        Vector3 normal = smallestEigenVector(cov);  // You'd implement or call a routine for this

        // Step 4: Ensure it's upward-facing (positive Z)
        if (normal.v[2] < 0) {
            for (int i = 0; i < 3; ++i) normal.v[i] *= -1;
        }

        return normal.normalized();
    }

}