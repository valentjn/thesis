// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteTextureSingle.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Texture3 : public TextureSingle
{
public:
    // Construction.
    Texture3(DFType format, unsigned int width, unsigned int height,
        unsigned int thickness, bool hasMipmaps = false,
        bool createStorage = true);

    // Texture dimensions.
    unsigned int GetWidth() const;
    unsigned int GetHeight() const;
    unsigned int GetThickness() const;
};

}
