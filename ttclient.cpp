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

bool has_code(const char* name) {
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

struct Module* find_code(const char* name) {
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
bool has_code(const char* name) {
    for (int i = 0; i < sizeof(FROZEN_MODULES) / sizeof(FROZEN_MODULES[0]); i++) {
        struct FrozenModule* frozen = &FROZEN_MODULES[i];
        if (strcmp(name, frozen->name) == 0) {
            return true;
        }
    }
    return false;
}

struct Module* find_code(const char* name) {
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

/* importer */


typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
} TTImportObject;

PyObject* TTImportFindModule(PyObject* self, PyObject* args) {
    DEBUG_PY(self);
    DEBUG_PY(args);
    
    const char* name;
    PyObject* path;
    
    if (!PyArg_ParseTuple(args, "s|O:find_module", &name, &path))
        return NULL;
    
    if (has_code(name))
        return self;
    else
        return Py_None;
}

PyObject* TTImportLoadModule(PyObject* self, PyObject* args) {
    DEBUG_PY(self);
    DEBUG_PY(args);
    
    const char* name;
    
    if (!PyArg_ParseTuple(args, "s:load_module", &name))
        return NULL;
    
    // check sys modules
    PyObject* modules = PyImport_GetModuleDict();
    PyObject* module = PyDict_GetItemString(modules, name);
    
    if (module) {
        Py_IncRef(module);
        return module;
    }
    
    struct Module* code = find_code(name);
    module = PyImport_AddModule(name);
    Py_IncRef(module);
    
    // module dict
    PyObject* dict = PyModule_GetDict(module);
    // add to sys modules
    PyDict_SetItemString(modules, name, module);
    
    // set values
    PyDict_SetItemString(dict, "__builtins__", PyEval_GetBuiltins());
    PyDict_SetItemString(dict, "__file__", PyString_FromString("<lambda>"));
    PyDict_SetItemString(dict, "__name__", PyString_FromString(name));
    PyDict_SetItemString(dict, "__path__", PyList_New(0));
    PyDict_SetItemString(dict, "__loader__", self);
    
    // Get package
    if (code->type == 1) {
        PyDict_SetItemString(dict, "__package__", PyString_FromString(name));
    } else {
        const char* index = strrchr(name, '.');
        char* parent = NULL;
        if (index) {
            size_t parentLen = index - name;
            parent = (char*)malloc(parentLen + 1);
            memcpy(parent, name, parentLen);
            parent[parentLen] = 0;
        }
        if (parent) {
            PyDict_SetItemString(dict, "__package__", PyString_FromString(parent));
            free(parent);
        } else {
            PyDict_SetItemString(dict, "__package__", PyString_FromString(""));
        }
    }
    
    
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
        // remove from sys modules in case of failure
        if (PyDict_GetItemString(modules, name))
            PyDict_DelItemString(modules, name);
        
        return NULL;
    }
    
    
    return module;
}

static PyMethodDef TTImportMethods[] = {
    {"find_module", (PyCFunction)TTImportFindModule, METH_CLASS | METH_VARARGS, 0, },
    {"load_module", (PyCFunction)TTImportLoadModule, METH_CLASS | METH_VARARGS, 0, },
    {NULL}  /* Sentinel */
};

static PyTypeObject TTImportType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "TTImport",                /* tp_name */
    sizeof(TTImportObject),    /* tp_basicsize */
    0,                         /* tp_itemsize */
    0,                         /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_compare */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,        /* tp_flags */
    0,                         /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    TTImportMethods,           /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
};

/* init */

int main(int argc, char** argv) {
    Py_NoSiteFlag = 1;
    
    Py_Initialize();
    PySys_SetArgv(argc, argv);
    PySys_SetPath("");
    
    if (PyType_Ready(&TTImportType) < 0)
        return 55;
    
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
    PyObject* metaPath = PySys_GetObject("meta_path");
    PyList_Append(metaPath, (PyObject*)&TTImportType);
    
    reveal(ENTRYPOINT, ENTRYPOINT_SIZE);
    PyRun_SimpleString((const char*)ENTRYPOINT);
    
    PyErr_Print();
    Py_Finalize();
}