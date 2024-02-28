
/*****************************************************************************

        Cobra128 3rd version of implementation
        Copyright (C) 1997 Markus Hahn

        Recoded by A.Myasnikow
        Web: www.darksoftware.narod.ru


        Block size: 128 bit
        Key size: 576 bit (default)


*******************************************************************************/

#include "string.h"
#include "stdlib.h"

/******************* Here you can set key material length **********************/
#define KEYSIZE_BYTES 72
/*******************************************************************************/


typedef unsigned long int u32;  /* unsigned 32bit */
typedef unsigned short int u16; /* unsigned 16bit */
typedef unsigned char u8;       /* unsigned 8bit */

/* pointer to basic data types */
typedef u32 *Pu32;
typedef u16 *Pu16;
typedef u8 *Pu8;


/* driver work context */
typedef struct
{
  /* boxes */
  u32 pbox[12][3];
  u32 sbox1[4][256];
  u32 sbox2[4][256];
  u32 sbox3[4][256];
  u32 wbox[2][4];

} Cobra128Ctx;





/* here we load init. data for the boxes */
#include "Cobra128.tab"

/* some macros, used to make the code more ledigble and to
   increase the speed by unrolling the loops... */

/* 32bit rotations, might be replaced by inline assembly */
#define ROTL32(a, i) (_lrotl((a),(i)))
#define ROTR32(a, i) (_lrotr((a),(i)))

/* the F function in a "compressed" form */
#define F(RESULT, Y, PBOX, SBOX) ulTemp = Y ^ PBOX;\
                                 RESULT = ( ( SBOX[0][ulTemp >> 24] +\
                                          SBOX[1][(ulTemp >> 16) & 0x0ff] ) ^\
                                              SBOX[2][(ulTemp >> 8) & 0x0ff] ) +\
                                                                              SBOX[3][ulTemp & 0x0ff];

/* one loop for encryption */
#define ENC_LOOP(LOOPNUM) ulSaveA = ulA;\
                          ulSaveB = ulB;\
                          ulSaveC = ulC;\
                          ulSaveD = ulD;\
                          ulD = ulSaveA;\
                          F(ulC, ulD, dCtx.pbox[LOOPNUM][2], dCtx.sbox3)\
                          ulC ^= ulSaveD;\
                          ulC = ROTR32(ulC, 1);\
                          F(ulB, ulC, dCtx.pbox[LOOPNUM][1], dCtx.sbox2)\
                          ulB ^= ulSaveC;\
                          ulB = ROTR32(ulB, 1);\
                          F(ulA, ulB, dCtx.pbox[LOOPNUM][0], dCtx.sbox1)\
                          ulA ^= ulSaveB;\
                          ulA = ROTR32(ulA, 1);

/* one loop for decryption */
#define DEC_LOOP(LOOPNUM) ulSaveA = ulA;\
                          ulSaveB = ulB;\
                          ulSaveC = ulC;\
                          ulSaveD = ulD;\
                          ulA = ulSaveD;\
                          F(ulB, ulSaveB, dCtx.pbox[LOOPNUM][0], dCtx.sbox1);\
                          ulB ^= ROTL32(ulSaveA, 1);\
                          F(ulC, ulSaveC, dCtx.pbox[LOOPNUM][1], dCtx.sbox2);\
                          ulC ^= ROTL32(ulSaveB, 1);\
                          F(ulD, ulSaveD, dCtx.pbox[LOOPNUM][2], dCtx.sbox3);\
                          ulD ^= ROTL32(ulSaveC, 1);


Cobra128Ctx dCtx;

/* the encryption routine */
void __stdcall __export
crypt (Pu32 blockToEncrypt)
{

  /* me must use the same variables as in the macros above */
  u32 ulTemp;
  u32 ulA, ulB, ulC, ulD;
  u32 ulSaveA, ulSaveB, ulSaveC, ulSaveD;

  /* copy the 128bit block to local variables, to increase the execution speed */
  ulA = blockToEncrypt[0];
  ulB = blockToEncrypt[1];
  ulC = blockToEncrypt[2];
  ulD = blockToEncrypt[3];

  /* whitening #1 */
  ulA ^= dCtx.wbox[0][0];
  ulB ^= dCtx.wbox[0][1];
  ulC ^= dCtx.wbox[0][2];
  ulD ^= dCtx.wbox[0][3];

  /* the encryption loop (unrolled) */

    ENC_LOOP (0)
    ENC_LOOP (1)
    ENC_LOOP (2)
    ENC_LOOP (3)
    ENC_LOOP (4)
    ENC_LOOP (5)
    ENC_LOOP (6)
    ENC_LOOP (7)
    ENC_LOOP (8)
    ENC_LOOP (9)
    ENC_LOOP (10)
    ENC_LOOP (11)
    
    /* whitening #2 */
  ulA ^= dCtx.wbox[1][0];
  ulB ^= dCtx.wbox[1][1];
  ulC ^= dCtx.wbox[1][2];
  ulD ^= dCtx.wbox[1][3];

  /* store the 128bit block back */
  blockToEncrypt[0] = ulA;
  blockToEncrypt[1] = ulB;
  blockToEncrypt[2] = ulC;
  blockToEncrypt[3] = ulD;
};


/* the decryption routine (nearly the same as above) */
void __stdcall __export
decrypt (Pu32 blockToEncrypt)
{

  u32 ulTemp;
  u32 ulA, ulB, ulC, ulD;
  u32 ulSaveA, ulSaveB, ulSaveC, ulSaveD;

  ulA = blockToEncrypt[0];
  ulB = blockToEncrypt[1];
  ulC = blockToEncrypt[2];
  ulD = blockToEncrypt[3];

  ulA ^= dCtx.wbox[1][0];
  ulB ^= dCtx.wbox[1][1];
  ulC ^= dCtx.wbox[1][2];
  ulD ^= dCtx.wbox[1][3];

    DEC_LOOP (11)
    DEC_LOOP (10)
    DEC_LOOP (9)
    DEC_LOOP (8)
    DEC_LOOP (7)
    DEC_LOOP (6)
    DEC_LOOP (5)
    DEC_LOOP (4)
    DEC_LOOP (3)
    DEC_LOOP (2)
    DEC_LOOP (1)
    DEC_LOOP (0)

  ulA ^= dCtx.wbox[0][0];
  ulB ^= dCtx.wbox[0][1];
  ulC ^= dCtx.wbox[0][2];
  ulD ^= dCtx.wbox[0][3];

  blockToEncrypt[0] = ulA;
  blockToEncrypt[1] = ulB;
  blockToEncrypt[2] = ulC;
  blockToEncrypt[3] = ulD;
};








void __stdcall __export
setup (Pu8 pKey)
{
  int nI, nJ, nK, nLoop;
  u16 unKeyPos;
  u32 azs[4];
  u32 ulBuf;
  Pu32 pHelpPtr;

  /* copy the init. data to the context */
  nK = 0;

  for (nJ = 0; nJ < 12; nJ++)
    {
      for (nI = 0; nI < 3; nI++)
        dCtx.pbox[nJ][nI] = box_init[nK++];
    };

  for (nJ = 0; nJ < 4; nJ++)
    {
      for (nI = 0; nI < 256; nI++)
        dCtx.sbox1[nJ][nI] = box_init[nK++];
    };

  for (nJ = 0; nJ < 4; nJ++)
    {
      for (nI = 0; nI < 256; nI++)
        dCtx.sbox2[nJ][nI] = box_init[nK++];
    };

  for (nJ = 0; nJ < 4; nJ++)
    {
      for (nI = 0; nI < 256; nI++)
        dCtx.sbox3[nJ][nI] = box_init[nK++];
    };

  for (nJ = 0; nJ < 2; nJ++)
    {
      for (nI = 0; nI < 4; nI++)
        dCtx.wbox[nJ][nI] = box_init[nK++];
    };

  /* xor the key over the boxes, warp around */
  unKeyPos = 0;
  /* xor the p-boxes */
  for (nJ = 0; nJ < 12; nJ++)
    {
      for (nI = 0; nI < 3; nI++)
        {
          for (nK = 0, ulBuf = 0; nK < 4; nK++)
            {
              if (unKeyPos >= KEYSIZE_BYTES)
                unKeyPos = 0;
              ulBuf = (ulBuf << 8) | (u32) (pKey[unKeyPos++] & 0x0ff);
            };
          dCtx.pbox[nJ][nI] ^= ulBuf;
        };
    };

  /* xor over the 1st S-Unit */
  for (nJ = 0; nJ < 4; nJ++)
    {
      for (nI = 0; nI < 256; nI++)
        {
          for (nK = 0; nK < 4; nK++)
            {
              if (unKeyPos >= KEYSIZE_BYTES)
                unKeyPos = 0;
              ulBuf = (ulBuf << 8) | (u32) (pKey[unKeyPos++] & 0x0ff);
            };
          dCtx.sbox1[nJ][nI] ^= ulBuf;
        };
    };

  /* xor over the 2nd S-Unit */
  for (nJ = 0; nJ < 4; nJ++)
    {
      for (nI = 0; nI < 256; nI++)
        {
          for (nK = 0; nK < 4; nK++)
            {
              if (unKeyPos >= KEYSIZE_BYTES)
                unKeyPos = 0;
              ulBuf = (ulBuf << 8) | (u32) (pKey[unKeyPos++] & 0x0ff);
            };
          dCtx.sbox2[nJ][nI] ^= ulBuf;
        };
    };

  /* xor over the 3rd S-Unit */
  for (nJ = 0; nJ < 4; nJ++)
    {
      for (nI = 0; nI < 256; nI++)
        {
          for (nK = 0; nK < 4; nK++)
            {
              if (unKeyPos >= KEYSIZE_BYTES)
                unKeyPos = 0;
              ulBuf = (ulBuf << 8) | (u32) (pKey[unKeyPos++] & 0x0ff);
            };
          dCtx.sbox3[nJ][nI] ^= ulBuf;
        };
    };


  for (nLoop = 0; nLoop < 2; nLoop++)
    {
      /* now we encrypt an all zero string and replace all boxes */
      azs[0] = azs[1] = azs[2] = azs[3] = 0x00000000;

      /* encrypt the pboxes */
      pHelpPtr = &dCtx.pbox[0][0];      /* (use a help pointer to access the boxes) */

      for (nI = 0; nI < 9; nI++)
        {
          crypt (azs);
          *(pHelpPtr++) = azs[0];
          *(pHelpPtr++) = azs[1];
          *(pHelpPtr++) = azs[2];
          *(pHelpPtr++) = azs[3];
        };

      /* encrypt the 1st S-Unit */
      pHelpPtr = &dCtx.sbox1[0][0];

      for (nI = 0; nI < 256; nI++)
        {
          crypt (azs);
          *(pHelpPtr++) = azs[0];
          *(pHelpPtr++) = azs[1];
          *(pHelpPtr++) = azs[2];
          *(pHelpPtr++) = azs[3];
        };

      /* encrypt the 2nd S-Unit */
      pHelpPtr = &dCtx.sbox2[0][0];

      for (nI = 0; nI < 256; nI++)
        {
          crypt (azs);
          *(pHelpPtr++) = azs[0];
          *(pHelpPtr++) = azs[1];
          *(pHelpPtr++) = azs[2];
          *(pHelpPtr++) = azs[3];
        };

      /* encrypt the 3rd S-Unit */
      pHelpPtr = &dCtx.sbox3[0][0];

      for (nI = 0; nI < 256; nI++)
        {
          crypt (azs);
          *(pHelpPtr++) = azs[0];
          *(pHelpPtr++) = azs[1];
          *(pHelpPtr++) = azs[2];
          *(pHelpPtr++) = azs[3];
        };

      /* encrypt the wboxes */
      pHelpPtr = &dCtx.wbox[0][0];

      for (nI = 0; nI < 2; nI++)
        {
          crypt (azs);
          *(pHelpPtr++) = azs[0];
          *(pHelpPtr++) = azs[1];
          *(pHelpPtr++) = azs[2];
          *(pHelpPtr++) = azs[3];
        };

      /* in the 1st loop: again do the same xoring as above,
         but this time only the p-boxes */
      if (nLoop == 0)
        {
          unKeyPos = 0;
          /* xor the p-boxes */
          for (nJ = 0; nJ < 12; nJ++)
            {
              for (nI = 0; nI < 3; nI++)
                {
                  for (nK = 0; nK < 4; nK++)
                    {
                      if (unKeyPos >= KEYSIZE_BYTES)
                        unKeyPos = 0;
                      ulBuf = (ulBuf << 8) | (u32) (pKey[unKeyPos++] & 0x0ff);
                    };
                  dCtx.pbox[nJ][nI] ^= ulBuf;
                };
            };
        };
    };


};


u32 __stdcall __export
getblocksize ()
{
  return 128;
}

u32 __stdcall __export
getkeysize ()
{
  return 576;
}

void __stdcall __export
getciphername (u8 * p)
{
  strcpy (p, "COBRA-128-576");
}
