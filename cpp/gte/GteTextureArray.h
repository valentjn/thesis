// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteTexture.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP TextureArray : public Texture
{
protected:
    // Abstract base class (shim).  All items in the array have the same
    // format, number of dimensions, dimension values, and mipmap status.
    TextureArray(unsigned int numItems, DFType format,
        unsigned int numDimensions, unsigned int dim0, unsigned int dim1,
        unsigned int dim2, bool hasMipmaps, bool createStorage);

public:
    // For use by the Shader class for storing reflection information.
    static int const shaderDataLookup = 5;
};

}
