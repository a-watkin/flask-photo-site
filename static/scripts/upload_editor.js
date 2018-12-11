"use strict";

const e = React.createElement;

class PhotosData extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      items: null,
      currentOffset: 20,
      selectedPhotos: [],
      albumId: null
    };

    // this.photoClick = this.photoClick.bind(this);
    this.DiscardPhoto = this.DiscardPhoto.bind(this);
  }

  componentWillMount() {
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("/");
    const albumId = splitUrl[5];

    fetch("http://127.0.0.1:5000/api/uploaded")
      .then(res => res.json())
      .then(
        result => {
          // console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos
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

  sendData() {
    console.log("getting here?", this.state.albumId, this.state.selectedPhotos);
    // /api/getphotos
    fetch("http://127.0.0.1:5000/api/getphotos", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        albumId: this.state.albumId,
        photos: this.state.selectedPhotos
      })
    }).then(() => {
      // redirect after successful post
      window.location.assign(
        `http://127.0.0.1:5000/albums/${this.state.albumId}`
      );
    });
  }

  DiscardPhoto(photo_id, key) {
    console.log("clicked discard", photo_id);

    let test = JSON.stringify({
      photoId: photo_id
    });

    console.log(test);

    fetch("http://127.0.0.1:5000/api/discard", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        photoId: photo_id
      })
    }).then(Response => {
      console.log("Response", Response.status);

      if (Response.status === 200) {
        let objectCopy = this.state.items;
        console.log("getting here ok");
        console.log(this.state.items);
        console.log(this.state.items[key]);
      }
    });
  }

  render() {
    let photo = null;
    let DiscardPhoto = this.DiscardPhoto;

    if (this.state.items) {
      let photos = this.state.items;
      // console.log(photos);
      let photo = Object.keys(photos).map(function(key, index) {
        let photo_url = photos[key]["original"];
        let photo_id = photos[key]["photo_id"];
        // console.log(photo_url);
        return (
          <div key={photos[key]["photo_id"]}>
            <div className="row">
              <div className="col">
                <img
                  src={photos[key]["original"]}
                  alt="Uploaded photo"
                  className="img-fluid"
                />
              </div>
              <div className="col text-center my-auto">
                <h5>Enter a title</h5>
                <input
                  className="input-group input-group-text"
                  type="text"
                  value={photos[key]["title"]}
                />
                <h6>{photos[key]["photo_id"]}</h6>
                <hr />
                <h5>Enter tags below</h5>
                <p>
                  You can enter multiple tags seperating them with commas. Tags
                  may contain spaces.
                </p>
                <input className="input-group input-group-text" type="text" />
                <hr />
                <button
                  className="btn btn-danger btn-lg"
                  onClick={() => DiscardPhoto(photo_id, key)}
                >
                  Discard photo
                </button>
              </div>
            </div>
            <hr />
          </div>
        );
      });

      return (
        <div>
          {photo}

          <div className="row">
            <div className="col text-left">
              <button className="btn btn-warning btn-lg">
                Add to a new album
              </button>
            </div>

            <div className="col text-right">
              <button className="btn btn-success btn-lg">
                Add to existing album
              </button>
            </div>
          </div>
          <hr />
        </div>
      );
    }

    return (
      <div>
        <h1>Hi from React</h1>

        {photo}
      </div>
    );
  }
}

const domContainer = document.querySelector("#upload-editor");
ReactDOM.render(e(PhotosData), domContainer);
