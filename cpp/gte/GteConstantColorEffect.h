// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.1 (2014/12/13)

#pragma once

#include <gte/GteMatrix4x4.h>
#include <gte/GteVisualEffect.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP ConstantColorEffect : public VisualEffect
{
public:
    // Construction.
    ConstantColorEffect(Vector4<float> const& color);

    // Member access.
    inline void SetPVWMatrix(Matrix4x4<float> const& pvwMatrix);
    inline Matrix4x4<float> const& GetPVWMatrix() const;

    // Required to bind and update resources.
    inline std::shared_ptr<ConstantBuffer> const& GetPVWMatrixConstant() const;
    inline std::shared_ptr<ConstantBuffer> const& GetColorConstant() const;

    // Naming support, used in the DX11 debug layer.  The default name is "".
    // If you want the name to show up in the DX11 destruction messages when
    // the associated DX11GraphicsObject is destroyed, set the name to
    // something other than "".
    virtual void SetName(std::string const& name);

private:
    // Vertex shader parameters.
    std::shared_ptr<ConstantBuffer> mPVWMatrixConstant;
    std::shared_ptr<ConstantBuffer> mColorConstant;

    // Convenience pointers.
    Matrix4x4<float>* mPVWMatrix;
    Vector4<float>* mColor;

    static std::string const msHLSLString;
};

//----------------------------------------------------------------------------
inline void ConstantColorEffect::SetPVWMatrix(
    Matrix4x4<float> const& pvwMatrix)
{
    *mPVWMatrix = pvwMatrix;
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& ConstantColorEffect::GetPVWMatrix() const
{
    return *mPVWMatrix;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<ConstantBuffer> const&
ConstantColorEffect::GetPVWMatrixConstant() const
{
    return mPVWMatrixConstant;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<ConstantBuffer> const&
ConstantColorEffect::GetColorConstant() const
{
    return mColorConstant;
}
//----------------------------------------------------------------------------

}
