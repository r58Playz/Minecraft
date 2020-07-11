
#define RANGE(a, b) unsigned a=0; a<b; a++

float fade(float t){
    float tmpl=t*6-15;
    float tmp=t*tmpl+10;
    return t*t*t*tmp;
};
float lerp(float t, float a, float b){
    float tmp = b-a;
    return a+t*tmp;
};
