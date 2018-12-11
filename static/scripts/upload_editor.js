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
    this.discardPhoto = this.discardPhoto.bind(this);
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

  discardPhoto(photo_id, key) {
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
        // let tempArray = [...this.state.items];
        // console.log("tempArray", tempArray);
        // tempAray.splice(key, 1);
        // this.setState({
        //   items: tempArray
        // });
        // let index = tempAray.indexOf(photo_id);
        let objectCopy = this.state.items;
        delete objectCopy[key];
        this.setState({
          items: objectCopy
        });
        console.log("getting here ok");
        console.log(this.state.items);
        // console.log(this.state.items[key]);
      }
    });
  }

  updateTitle(e, photo_id, key) {
    console.log("updateTitle called", e.target.value, photo_id, key);

    let test = JSON.stringify({
      photoId: photo_id
    });

    console.log(test);

    fetch("http://127.0.0.1:5000/api/uploaded/title", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        photoId: photo_id,
        title: e.target.value
      })
    }).then(Response => {
      console.log("Response", Response.status);

      if (Response.status === 200) {
        let objectCopy = this.state.items;
        objectCopy[key]["photo_title"] = e.target.value;

        this.setState({
          items: objectCopy
        });
      }
    });
  }

  addTags(e, photo_id, key) {
    console.log("hello from addTags");
    console.log(e.target.value);

    if (e.target.value) {
      let test = JSON.stringify({
        photoId: photo_id,
        tagValues: e.target.value
      });

      console.log(test);

      fetch("http://127.0.0.1:5000/api/add/tags", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          photoId: photo_id,
          tagValues: e.target.value
        })
      }).then(Response => {
        console.log("Response", Response.status);

        if (Response.status === 200) {
          console.log(Response);
          let objectCopy = this.state.items;
          console.log("wtf");

          console.log(objectCopy);

          // let test = [e.target.value, ...objectCopy[key]["tags"]];
          // console.log("test", test);
          //   objectCopy[key]["tags"] = e.target.value;

          //   this.setState({
          //     items: objectCopy
        }
      });
    }
  }

  render() {
    let photo = null;
    let discardPhoto = this.discardPhoto;
    let updateTitle = this.updateTitle;
    let addTags = this.addTags;

    if (this.state.items) {
      let photos = this.state.items;
      // console.log(photos);
      let photo = Object.keys(photos).map(function(key) {
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
                  placeholder={
                    photos[key]["photo_title"] === null
                      ? ""
                      : photos[key]["photo_title"]
                  }
                  defaultValue={
                    photos[key]["photo_title"] === null
                      ? ""
                      : photos[key]["photo_title"]
                  }
                  onBlur={e => updateTitle(e, photo_id, key)}
                />
                <h6>{photos[key]["photo_id"]}</h6>
                <hr />
                <h5>Enter tags below</h5>
                <p>
                  You can enter multiple tags seperating them with commas. Tags
                  may contain spaces.
                </p>
                <input
                  className="input-group input-group-text"
                  type="text"
                  onBlur={e => addTags(e, photo_id, key)}
                  placeholder={photos[key]["tags"]}
                  defaultValue={photos[key]["tags"]}
                />
                <hr />
                <button
                  className="btn btn-danger btn-lg"
                  onClick={() => discardPhoto(photo_id, key)}
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
