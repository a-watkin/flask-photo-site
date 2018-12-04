"use strict";

const e = React.createElement;

class PhotosData extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      items: null,
      currentOffset: 20,
      selectedPhotos: []
    };
  }

  componentWillMount() {
    fetch("http://127.0.0.1:5000/api/getphotos")
      .then(res => res.json())
      .then(
        result => {
          // console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  getNextPhotos() {
    console.log("next called ", this.state.currentOffset);

    fetch(
      `http://127.0.0.1:5000/api/getphotos?offset=${this.state.currentOffset +
        20}`
    )
      .then(res => res.json())
      .then(
        result => {
          console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  getPreviousPhotos() {
    console.log("previous called ", this.state.currentOffset);

    if (this.state.currentOffset <= 0) {
      return false;
    }

    fetch(
      `http://127.0.0.1:5000/api/getphotos?offset=${this.state.currentOffset -
        20}`
    )
      .then(res => res.json())
      .then(
        result => {
          console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  photoClick(photo_id) {
    console.log("Greetings from photoClick the photo_id is ", photo_id);
  }

  render() {
    let cardStyle = {
      width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px"
      // webkitBoxAlign: "center",
      // webkitBoxPack: "center",
      // display: "-webkit-box"
    };

    let large_square = "";
    // it doesn't seemt to be able to get this reference
    // without delaring it here from the Objct.keys reurn statment
    // also passing it and invoking leads to it being executed twice?
    let photoClick = this.photoClick;

    if (this.state.items) {
      large_square = this.state.items[0]["large_square"];
      const photos = this.state.items;

      console.log(this.state.items[0]["large_square"]);
      let test = Object.keys(photos).map(function(key, index) {
        if (index % 5 === 0) {
          console.log("eh");
          // conditionally add columns?
        }
        // console.log();
        return (
          <div
            key={photos[key]["photo_id"]}
            className="col text-right"
            // not ideal right here...but it works
            onClick={() => photoClick(photos[key]["photo_id"])}
          >
            <div id="photo-select" style={cardStyle} className="card">
              <div className="card-header">
                <h5 className="card-title text-center">
                  {photos[key]["photo_title"]}
                </h5>
              </div>

              <div className="card-body">
                <img
                  src={photos[key]["large_square"]}
                  alt="Responsive image"
                  className="card-img-top"
                />
              </div>
            </div>
          </div>
        );
      });

      console.log(test);

      return (
        <div>
          <div className="row text-center">
            <div className="col">
              <button
                className="btn btn-lg"
                onClick={() => this.getPreviousPhotos()}
              >
                Next
              </button>
            </div>
            <div className="col">
              <button
                className="btn btn-lg"
                onClick={() => this.getNextPhotos()}
              >
                Previous
              </button>
            </div>
          </div>

          <hr />

          <div className="row"> {test} </div>
        </div>
      );
    }

    return (
      <div className="row">
        <div className="col">
          <h1>Some problem with getting the data.</h1>
        </div>
      </div>
    );
  }
}

const domContainer = document.querySelector("#photos-selector");
ReactDOM.render(e(PhotosData), domContainer);
