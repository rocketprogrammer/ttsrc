#include "Python.h"
#include "marshal.h"
#include "ttmodules.h"

#ifdef TTDEBUG
    #define DEBUG() printf("[-] %s:%d, in %s\n", __FILE__, __LINE__, __FUNCTION__)
    #define DEBUG_PY(obj) printf("[P] %s:%d, in %s => %s\n", __FILE__, __LINE__, __FUNCTION__, PyString_AsString(PyObject_Repr(obj)));
    #define DEBUG_STR(str) printf("[S] %s:%d, in %s => %s\n", __FILE__, __LINE__, __FUNCTION__, str);
#else
    #define DEBUG()
    #define DEBUG_PY(obj)
    #define DEBUG_STR(str)
#endif

PyObject* orig_import;

struct Module {
    char* name;
    PyCodeObject* code;
    int type;
};

void reveal(unsigned char* data, unsigned int length) {
    unsigned char last = 99;
    for (unsigned int index = 0; index < length; index++) {
        last = data[index] + last;
        data[index] = last;
    }
}

void reveal_str(unsigned char* data) {
    unsigned char last = 99;
    for (unsigned int index = 0;; index++) {
        last = data[index] + last;
        data[index] = last;
        if (last == 0)
            break;
    }
}

#ifndef FROZEN_ENABLED 
struct Element {
    struct Module value;
    struct Element* left;
    struct Element* right;
};

struct Element* code_tree;

void add_code(char* name, PyCodeObject* code, int type) {
    struct Element* element = (struct Element*)malloc(sizeof(struct Element));
    element->value.name = name;
    element->value.code = code;
    element->value.type = type;
    element->left = NULL;
    element->right = NULL;
    
    if (code_tree == NULL) {
        code_tree = element;
        
    } else {
        struct Element* current = code_tree;
        while (1) {            
            int diff = strcmp(name, current->value.name);
            
            if (diff < 0) {
                if (current->left == NULL) {
                    current->left = element;
                    return;
                } else {
                    current = current->left;
                }
            }
            else if (diff > 0) {
                if (current->right == NULL) {
                    current->right = element;
                    return;
                } else {
                    current = current->right;
                }
            }
        }
    }
}

bool has_code(char* name) {
    struct Element* current = code_tree;
    while (1) {
        int diff;
        if (current == NULL)
            return NULL;
        
        diff = strcmp(name, current->value.name);
        
        if (diff < 0)
            current = current->left;
        else if (diff > 0)
            current = current->right;
        else
            return true;
    }
    return false;
}

struct Module* find_code(char* name) {
    struct Element* current = code_tree;
    while (1) {
        int diff;
        if (current == NULL)
            return NULL;
        
        diff = strcmp(name, current->value.name);
        
        if (diff < 0)
            current = current->left;
        else if (diff > 0)
            current = current->right;
        else
            return &current->value;
    }
    return NULL;
}
#else
bool has_code(char* name) {
    for (int i = 0; i < sizeof(FROZEN_MODULES) / sizeof(FROZEN_MODULES[0]); i++) {
        struct FrozenModule* frozen = &FROZEN_MODULES[i];
        if (strcmp(name, frozen->name) == 0) {
            return true;
        }
    }
    return false;
}

struct Module* find_code(char* name) {
    for (int i = 0; i < sizeof(FROZEN_MODULES) / sizeof(FROZEN_MODULES[0]); i++) {
        struct FrozenModule* frozen = &FROZEN_MODULES[i];
        if (strcmp(name, frozen->name) == 0) {
            struct Module* module = (struct Module*)malloc(sizeof(struct Module));
            module->name = frozen->name;
            module->code = (PyCodeObject*)PyMarshal_ReadObjectFromString(frozen->code, frozen->length);
            module->type = frozen->type;
            return module;
        }
    }
    return NULL;
}
#endif

void print(PyObject* obj) {
    printf("%s\n", PyString_AsString(PyObject_Repr(obj)));
}

PyObject* create(char* name, int force) {
    PyObject* modules = PyImport_GetModuleDict();
    PyObject* module = PyDict_GetItemString(modules, name);
    PyObject* dict;
    struct Module* code;
    
    if (module) {
        Py_IncRef(module);
        return module;
    }
    
    code = find_code(name);
    if (code == NULL) {
        if (force)
            return PyImport_AddModule(name);
        else
            return NULL;
    }
    
    module = PyImport_AddModule(name);
    Py_IncRef(module);
    
    // Get parent
    char* index = strrchr(name, '.');
    char* parent = NULL;
    PyObject* parentModule = NULL;
    if (index) {
        size_t parentLen = index - name;
        parent = (char*)malloc(parentLen + 1);
        memcpy(parent, name, parentLen);
        parent[parentLen] = 0;
        parentModule = create(parent, 1);
    }
    
    DEBUG_STR(parent);
    DEBUG_PY(parentModule);
    
    dict = PyModule_GetDict(module);
    
    PyDict_SetItemString(dict, "__builtins__", PyEval_GetBuiltins());
    PyDict_SetItemString(dict, "__file__", PyString_FromString(name));
    
    if (code->type == 1) {
        PyDict_SetItemString(dict, "__package__", PyString_FromString(name));
    } else if (parent) {
        PyDict_SetItemString(dict, "__package__", PyString_FromString(parent));
    } else {
        PyDict_SetItemString(dict, "__package__", PyString_FromString(""));
    }
    
    if (parentModule)
        PyDict_SetItemString(PyModule_GetDict(parentModule), index + 1, module);
    
    if (PyEval_EvalCode(code->code, dict, dict) == NULL) {
#ifdef TTDEBUG
        PyObject* ptype;
        PyObject* pvalue;
        PyObject* ptraceback;
        PyErr_Fetch(&ptype, &pvalue, &ptraceback);
        printf("An error occured somehow (module %s)\n\n", name);
        PyErr_Display(ptype, pvalue, ptraceback);
        PyErr_Restore(ptype, pvalue, ptraceback);
        printf("\n");
#endif
        if (PyDict_DelItemString(modules, name))
            PyDict_DelItemString(modules, name);
        return NULL;
    }
    
    if (parent)
        free(parent);
    
    //Py_DecRef(module);
    
    return module;
}

PyObject* importer(PyObject* self, PyObject* args, PyObject* kwds) {
    char* name;
    PyObject* globals = NULL;
    PyObject* locals = NULL;
    PyObject* fromlist = NULL;
    int level = -1;
    
    static char* kwlist[] = {"name", "globals", "locals", "fromlist", "level", 0};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|OOOi:__import__", kwlist, &name, &globals, &locals, &fromlist, &level))
        return NULL;
        
    PyObject* package = NULL;
    PyObject* module = NULL;
    char* fullname = NULL;
    
    DEBUG();
    // Is the module relative?
    if (globals && PyDict_Check(globals)) {
        package = PyDict_GetItemString(globals, "__package__");
        if (package && PyString_Check(package)) {
            fullname = (char*)malloc(PyString_Size(package) + strlen(name) + 2);
            fullname[0] = 0;
            
            strcat(fullname, PyString_AsString(package));
            strcat(fullname, ".");
            strcat(fullname, name);
            
            // Do we have its code?
            if (!has_code(fullname)) {
                free(fullname);
                fullname = NULL;
                package = NULL;
            }
        } else {
            package = NULL;
        }
    }
    
    DEBUG();
    // Is the module absolute?
    if (!fullname) {
        if (!has_code(name)) {
            DEBUG_STR(name);
            return PyObject_Call(orig_import, args, kwds);
        }
        
        fullname = name;
    }

    module = create(fullname, 0);

    DEBUG_PY(module);
    if (fromlist && PyObject_IsTrue(fromlist)) {
        DEBUG();
        PyObject* iterator = PyObject_GetIter(fromlist);
        PyObject* item;
        while (item = PyIter_Next(iterator)) {
            if (PyString_Check(item)) {
                // Attempt to import every element in fromlist
                // (from toontown.toonbase import ToontownStart
                //  will look for toontown.toonbase.ToontownStart)
                
                char* tempname = (char*)malloc(strlen(fullname) + PyString_Size(item) + 2);
                tempname[0] = 0;
                DEBUG();
                strcat(tempname, fullname);
                strcat(tempname, ".");
                strcat(tempname, PyString_AsString(item));
                DEBUG_STR(tempname);
                DEBUG_STR(has_code(tempname) ? "^ has code" : "^ not");
                if (has_code(tempname))
                    create(tempname, 0);
                
                free(tempname);
            }
        }
        
    } else {
        DEBUG();
        // We must return the first part of the name.
        char* modulename;
        char* index = strchr(name, '.');
        if (index) {
            DEBUG();
            if (package) {
                // We have a package. This means we returns a submodule
                modulename = (char*)malloc(PyString_Size(package) + index - name + 2);
                modulename[0] = 0;
                
                // {package}.{name}
                strcat(modulename, PyString_AsString(package));
                strcat(modulename, ".");
                strncat(modulename, name, index - name);
                
            } else {
                // We are package free
                DEBUG();
                modulename = (char*)malloc(index - name + 1);
                memcpy(modulename, name, index - name);
                modulename[index - name] = 0;
            }
            
            DEBUG_STR(modulename);
            module = create(modulename, 0);
            free(modulename);
            DEBUG_PY(module);
        }
    }
    
    DEBUG();
    return module;
}

int main(int argc, char** argv) {
    Py_NoSiteFlag = 1;
    
    Py_Initialize();
    PySys_SetArgv(argc, argv);
    PySys_SetPath("");
    
#ifndef FROZEN_ENABLED
    FILE* fp = fopen("Toontown.bin", "rb");
    fseek(fp, 0, SEEK_END);
    size_t size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    
    while (ftell(fp) < size) {
        char header[7];
        unsigned char moduleType;
        unsigned short nameLen;
        unsigned int codeLen;
        char* buffer;
        char* name;
        char* code;
        PyCodeObject* codeObj;
        
        fread(header, 1, 7, fp);
        
        moduleType = *(unsigned char*)(header);
        nameLen = *(unsigned short*)(header + 1);
        codeLen = *(unsigned int*)(header + 3);
        
        name = (char*)malloc(nameLen+1);
        name[nameLen] = 0;
        fread(name, 1, nameLen, fp);
        
        code = (char*)malloc(codeLen);
        fread(code, 1, codeLen, fp);
        
        codeObj = (PyCodeObject*)PyMarshal_ReadObjectFromString(code, codeLen);
        
        add_code(name, codeObj, moduleType);
        free(code);
    }
    
    fclose(fp);
#endif
    
    PyMethodDef import = {"__tt_import__", (PyCFunction)importer, METH_VARARGS | METH_KEYWORDS, NULL};
    
    PyObject* builtins = PyEval_GetBuiltins();
    orig_import = PyDict_GetItemString(builtins, "__import__");
    PyDict_SetItemString(builtins, "__import__", PyCFunction_New(&import, NULL));
    
    reveal(ENTRYPOINT, ENTRYPOINT_SIZE);
    PyRun_SimpleString((const char*)ENTRYPOINT);
    
    PyErr_Print();
    Py_Finalize();
}