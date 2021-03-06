// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteDX11Texture.h>
#include <gte/GteTextureSingle.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP DX11TextureSingle : public DX11Texture
{
public:
    // Abstract base class, a shim to distinguish between single textures and
    // texture arrays.
    virtual ~DX11TextureSingle();
protected:
    // No public construction.  Derived classes use this constructor.
    DX11TextureSingle(TextureSingle const* gtTextureSingle);

public:
    // Member access.
    TextureSingle* GetTextureSingle() const;
};

}
