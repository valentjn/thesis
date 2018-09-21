// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.2.1 (2014/12/13)

#pragma once

#include <gte/GteLightingConstants.h>
#include <gte/GteVisualEffect.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP LightingEffect : public VisualEffect
{
public:
    // Abstract base class.
    virtual ~LightingEffect();
protected:
    // Construction.  The shader is selected either for per-vertex lighting
    // or per-pixel lighting.
    LightingEffect(LightingConstants const& lighting,
        std::string const& hlslString, bool perVertex);

public:
    // Member access.
    inline void SetPVWMatrix(Matrix4x4<float> const& pvwMatrix);
    inline Matrix4x4<float> const& GetPVWMatrix() const;
    inline Matrix4x4<float>& GetPVWMatrix();
    inline void SetLighting(LightingConstants const& lighting);
    inline LightingConstants const& GetLighting() const;
    inline LightingConstants& GetLighting();

    // Required to bind and update resources.
    inline std::shared_ptr<ConstantBuffer> const& GetPVWMatrixConstant()
        const;
    inline std::shared_ptr<ConstantBuffer> const& GetLightingConstant() const;

    // Naming support, used in the DX11 debug layer.  The default name is "".
    // If you want the name to show up in the DX11 destruction messages when
    // the associated DX11GraphicsObject is destroyed, set the name to
    // something other than "".
    virtual void SetName(std::string const& name);

protected:
    // Vertex shader parameters.
    std::shared_ptr<ConstantBuffer> mPVWMatrixConstant;
    std::shared_ptr<ConstantBuffer> mLightingConstant;

    // Convenience pointers.
    Matrix4x4<float>* mPVWMatrix;
    LightingConstants* mLighting;
};

//----------------------------------------------------------------------------
inline void LightingEffect::SetPVWMatrix(Matrix4x4<float> const& pvwMatrix)
{
    *mPVWMatrix = pvwMatrix;
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& LightingEffect::GetPVWMatrix() const
{
    return *mPVWMatrix;
}
//----------------------------------------------------------------------------
inline Matrix4x4<float>& LightingEffect::GetPVWMatrix()
{
    return *mPVWMatrix;
}
//----------------------------------------------------------------------------
inline void LightingEffect::SetLighting(LightingConstants const& lighting)
{
    *mLighting = lighting;
}
//----------------------------------------------------------------------------
inline LightingConstants const& LightingEffect::GetLighting() const
{
    return *mLighting;
}
//----------------------------------------------------------------------------
inline LightingConstants& LightingEffect::GetLighting()
{
    return *mLighting;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<ConstantBuffer> const&
LightingEffect::GetPVWMatrixConstant() const
{
    return mPVWMatrixConstant;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<ConstantBuffer> const&
LightingEffect::GetLightingConstant() const
{
    return mLightingConstant;
}
//----------------------------------------------------------------------------

}
