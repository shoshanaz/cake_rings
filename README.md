# cake_rings
An Inkscape 1.4 Extension that shows the rings needed to construct a round cake with a picture when a slice is cut.

In the spirit of the iconic checkerboard cakes, it is possible to construct a cake that shows a (albeit very pixelized) picture when cut. This is accomplished by using layered nested rings of the desired cake colors. Not a process for the faint-hearted baker! This extension helps by showing what rings are required to do the cake picture. 

To use it, create a matrix of squares (using tiled clones helps) and color the squares to show what the image should look like when cut. Group all those colored squares together. Be sure you don't have extra squares anywhere, or it will not work. If you have a nine by nine matrix, you should have 81 squares. Then apply the extension. You can specify how what size each square represents.

To install, just put the cake-rings.inx and cake_rings.py in your Inkscape extension folder and restart Inkscape. I have included a sample starting file to give you the idea: cake_idea.svg

Note: This was developed using Gemini, so all normal caveats that go in that direction.
