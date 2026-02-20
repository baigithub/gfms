"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.defaults = void 0;
exports.getOptions = getOptions;
const tslib_1 = require("tslib");
const common_1 = require("../common");
const config_1 = require("../config");
const shape_1 = require("../shape");
function getOptions(options) {
    const { grid, panning, mousewheel, embedding } = options, others = tslib_1.__rest(options
    // size
    // ----
    , ["grid", "panning", "mousewheel", "embedding"]);
    // size
    // ----
    const container = options.container;
    if (container != null) {
        if (others.width == null) {
            others.width = container.clientWidth;
        }
        if (others.height == null) {
            others.height = container.clientHeight;
        }
    }
    else {
        throw new Error(`Ensure the container of the graph is specified and valid`);
    }
    const result = common_1.ObjectExt.merge({}, exports.defaults, others);
    // grid
    // ----
    const defaultGrid = { size: 10, visible: false };
    if (typeof grid === 'number') {
        result.grid = { size: grid, visible: false };
    }
    else if (typeof grid === 'boolean') {
        result.grid = Object.assign(Object.assign({}, defaultGrid), { visible: grid });
    }
    else {
        result.grid = Object.assign(Object.assign({}, defaultGrid), grid);
    }
    // booleas
    // -------
    const booleas = [
        'panning',
        'mousewheel',
        'embedding',
    ];
    booleas.forEach((key) => {
        const val = options[key];
        if (typeof val === 'boolean') {
            result[key].enabled = val;
        }
        else if (val != null) {
            result[key] = Object.assign(Object.assign({}, result[key]), val);
        }
    });
    return result;
}
exports.defaults = {
    x: 0,
    y: 0,
    scaling: {
        min: 0.01,
        max: 16,
    },
    grid: {
        size: 10,
        visible: false,
    },
    background: false,
    panning: {
        enabled: true,
        eventTypes: ['leftMouseDown'],
    },
    mousewheel: {
        enabled: false,
        factor: 1.2,
        zoomAtMousePosition: true,
    },
    highlighting: {
        default: {
            name: 'stroke',
            args: {
                padding: 3,
            },
        },
        nodeAvailable: {
            name: 'className',
            args: {
                className: config_1.Config.prefix('available-node'),
            },
        },
        magnetAvailable: {
            name: 'className',
            args: {
                className: config_1.Config.prefix('available-magnet'),
            },
        },
    },
    connecting: {
        snap: false,
        allowLoop: true,
        allowNode: true,
        allowEdge: false,
        allowPort: true,
        allowBlank: true,
        allowMulti: true,
        highlight: false,
        anchor: 'center',
        edgeAnchor: 'ratio',
        connectionPoint: 'boundary',
        router: 'normal',
        connector: 'normal',
        validateConnection({ type, sourceView, targetView }) {
            const view = type === 'target' ? targetView : sourceView;
            return view != null;
        },
        createEdge() {
            return new shape_1.Edge();
        },
    },
    translating: {
        restrict: false,
    },
    embedding: {
        enabled: false,
        findParent: 'bbox',
        frontOnly: true,
        validate: () => true,
    },
    moveThreshold: 0,
    clickThreshold: 0,
    magnetThreshold: 0,
    preventDefaultDblClick: true,
    preventDefaultMouseDown: false,
    preventDefaultContextMenu: true,
    preventDefaultBlankAction: true,
    interacting: {
        edgeLabelMovable: false,
    },
    async: true,
    virtual: false,
    guard: () => false,
};
//# sourceMappingURL=options.js.map