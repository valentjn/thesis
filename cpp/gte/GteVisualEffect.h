// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.2 (2015/04/30)

#pragma once

#include <gte/GteGeometryShader.h>
#include <gte/GtePixelShader.h>
#include <gte/GteVertexShader.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP VisualEffect
{
public:
    // Construction and destruction.
    virtual ~VisualEffect();
    VisualEffect(
        std::shared_ptr<VertexShader> const& vshader =
            std::shared_ptr<VertexShader>(),
        std::shared_ptr<PixelShader> const& pshader =
            std::shared_ptr<PixelShader>(),
        std::shared_ptr<GeometryShader> const& gshader =
            std::shared_ptr<GeometryShader>());

    // Member access.
    inline std::shared_ptr<VertexShader> const& GetVertexShader() const;
    inline std::shared_ptr<GeometryShader> const& GetGeometryShader() const;
    inline std::shared_ptr<PixelShader> const& GetPixelShader() const;

    // Naming support, used in the DX11 debug layer.  The default name is "".
    // If you want the name to show up in the DX11 destruction messages when
    // the associated DX11GraphicsObject is destroyed, set the name to
    // something other than "".
    virtual void SetName(std::string const& name);
    inline std::string const& GetName() const;

protected:
    std::string mName;
    std::shared_ptr<VertexShader> mVShader;
    std::shared_ptr<PixelShader> mPShader;
    std::shared_ptr<GeometryShader> mGShader;
};

//----------------------------------------------------------------------------
inline std::shared_ptr<VertexShader> const&
VisualEffect::GetVertexShader() const
{
    return mVShader;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<GeometryShader> const&
VisualEffect::GetGeometryShader() const
{
    return mGShader;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<PixelShader> const&
VisualEffect::GetPixelShader() const
{
    return mPShader;
}
//----------------------------------------------------------------------------
inline std::string const& VisualEffect::GetName() const
{
    return mName;
}
//----------------------------------------------------------------------------

}
