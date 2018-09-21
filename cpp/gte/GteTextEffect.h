// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteConstantBuffer.h>
#include <gte/GteSamplerState.h>
#include <gte/GteTexture2.h>
#include <gte/GteVector4.h>
#include <gte/GteVisualEffect.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP TextEffect : public VisualEffect
{
public:
    // Construction.
    TextEffect(std::shared_ptr<Texture2> const& texture);

    // Support for typesetting.
    std::shared_ptr<ConstantBuffer> const& GetTranslate() const;
    std::shared_ptr<ConstantBuffer> const& GetColor() const;
    void SetTranslate(float x, float y);
    void SetColor(Vector4<float> const& color);

    // Naming support, used in the DX11 debug layer.  The default name is "".
    // If you want the name to show up in the DX11 destruction messages when
    // the associated DX11GraphicsObject is destroyed, set the name to
    // something other than "".
    virtual void SetName(std::string const& name);

private:
    std::shared_ptr<ConstantBuffer> mTranslate;
    std::shared_ptr<ConstantBuffer> mColor;
    std::shared_ptr<SamplerState> mSamplerState;
    static std::string const msHLSLString;
};

}
