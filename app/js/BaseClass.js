class VectorN {
    /** @param {number[]} array */
    constructor(array) {
        this.array = array;
    }

    /** @param {VectorN} v */
    plus(v) {
        return new VectorN(this.array.map((x, i) => x + v.array[i]));
    }

    /** @param {VectorN} v */
    minus(v) {
        return new VectorN(this.array.map((x, i) => x - v.array[i]));
    }

    /** @param {number} k */
    times(k) {
        return new VectorN(this.array.map(x => x * k));
    }

    /** @param {number} k */
    divide(k) {
        return new VectorN(this.array.map(x => x / k));
    }

    /** @param {VectorN} v */
    dot(v) {
        return this.array.reduce((sum, x, i) => sum + x * v.array[i], 0);
    }
}

class Vertex {

    /** @type {Edge[]} */ edges = [];

    /**
     * @param {number} id
     * @param {any} data
    */
    constructor(id, data) {
      this.id = id;
      this.data = data;
    }

    /** @return {Arrow[]} */
    getArrows() {
        // @ts-ignore
        return this.edges.filter(edge => edge instanceof Arrow);
    }

    /** @param {Vertex} vertex */
    isParent(vertex) {
        const Arrows = this.getArrows();
        return Arrows.some(arrow => arrow.start === vertex);
    }

    /** @param {Vertex} vertex */
    isChild(vertex) {
        const Arrows = this.getArrows();
        return Arrows.some(arrow => arrow.end === vertex);
    }

    
}
  
class Edge {

    /**
     * @param {Vertex} vertex1 
     * @param {Vertex} vertex2 
     * @param {VectorN} weight 
     * */
    constructor(vertex1, vertex2, weight) {
        this.vertex1 = vertex1;
        this.vertex2 = vertex2;
        this.weight = weight;
    }

    /** 
     * @param {Vertex} vertex
     * @return {Vertex}
     * */
    getContrastVertex(vertex) {
        if (this.vertex1 === vertex) {
            return this.vertex2;
        } else {
            return this.vertex1;
        }
    }

    
}

class Arrow extends Edge {

    /**
     * 
     * @param {Vertex} vertex_start 
     * @param {Vertex} vertex_end
     * @param {VectorN} weight 
     */
    constructor(vertex_start, vertex_end, weight) {
        super(vertex_start, vertex_end, weight);
        this.start = vertex_start;
        this.end = vertex_end;
    }


}
  
class Graph {
    constructor(isDirected = false) {
      this.vertices = {};
      this.edges = [];
      this.isDirected = isDirected;
    }
  
    addVertex(vertex) {
      this.vertices[vertex.id] = vertex;
    }
  
    addEdge(edge) {
      this.edges.push(edge);
    }
  
    // その他のグラフ操作メソッド...
}
  
class GraphView {
    constructor(graph) {
      this.graph = graph;
    }
  
    // グラフを描画するメソッド...
}

class ElementCreater {
    static domParser = new DOMParser();

    /**
     * 
     * htmlの文字列からそれと同じHTMLElementを生成する。ただし、htmlの文字列は1つの要素であること。（1つの要素の中に複数の子要素がネストされている構造が許される）
     * 複数エレメントを含むhtml文字列をまとめて作りたい場合は createElementsFromHTMLSting() を使うこと。
     * 良い例:
     * <div class="output_text">
     *      <p>おはよう</p>
     * </div>'。
     * この場合output_textのdiv要素全体が返される。
     * 
     * ダメな例:
     * <div class="output_text1"><p>おはよう</p>'</div>
     * <div class="output_text2"><p>コンバンワ</p>'</div>
     * @param {string} html 
     * @return {HTMLElement}
     */
    static createElementFromHTMLSting(html) {
        const parsedDocument = ElementCreater.domParser.parseFromString(html, 'text/html');
        const firstChild = parsedDocument.body.firstChild;
        if (firstChild && firstChild instanceof HTMLElement) {
            return firstChild; // HTMLElementとして返す
        } else {
            throw new Error('Parsed element is not an HTMLElement.');
        }
    }

    /**
     * 複数のエレメントを含むhtml文字列からそれと同じHTMLElementを生成する。
     * @param {string} html
     * @return {HTMLCollection} getElementsByClassName()で取得できるようなものと同じ型。
     */
    static createElementsFromHTMLSting(html) {
        const parsedDocument = ElementCreater.domParser.parseFromString(html, 'text/html');
        const children = parsedDocument.body.children;
        if (children) {
            return children; // HTMLCollectionとして返す
        } else {
            throw new Error('Parsed element is not an HTMLElement.');
        }
    }

    /**
     * htmlの文字列からそれと同じDocumentを生成する。
     * @param {string} html
     * @return {Document}
     */
    static createnewDocumentFromHTMLString(html) {
        return ElementCreater.domParser.parseFromString(html, 'text/html');
    }
}
